
import unittest

from tbk.soap.exceptions import SoapClientException, SoapServerException
from tbk.soap import SoapRequestor, SoapRequest, SoapResponse, SoapClient

from .utils import mock


class SoapRequestorTest(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        super(SoapRequestorTest, self).__init__(*args, **kwargs)
        self.addTypeEqualityFunc(SoapResponse, 'assert_equal_response')
        self.addTypeEqualityFunc(SoapRequest, 'assert_equal_request')

    def setUp(self):
        self.soap_client = mock.MagicMock(spec=SoapClient)

    def test_get_enum_value(self):
        get_enum_value = self.soap_client.get_enum_value

        requestor = SoapRequestor(self.soap_client)
        result = requestor.get_enum_value('EnumType', 'value')

        get_enum_value.assert_called_once_with(
            'EnumType',
            'value')
        self.assertEqual(get_enum_value.return_value, result)

    def test_get_enum_value_exception(self):
        get_enum_value = self.soap_client.get_enum_value
        get_enum_value.side_effect = SoapClientException

        requestor = SoapRequestor(self.soap_client)

        self.assertRaises(
            SoapClientException, requestor.get_enum_value, 'EnumType', 'value')

    def test_create_object(self):
        create_object = self.soap_client.create_object

        requestor = SoapRequestor(self.soap_client)
        result = requestor.create_object('TypeName', 'arg', kw='kw')

        create_object.assert_called_once_with(
            'TypeName',
            'arg',
            kw='kw')
        self.assertEqual(create_object.return_value, result)

    def test_create_object_exception(self):
        create_object = self.soap_client.create_object
        create_object.side_effect = SoapClientException

        requestor = SoapRequestor(self.soap_client)

        self.assertRaises(
            SoapClientException, requestor.create_object, 'TypeName', 'arg', kw='kw')

    def test_request(self):
        request = self.soap_client.request
        mocked_result = mock.Mock()
        mocked_envelope_sent = mock.Mock()
        mocked_envelope_received = mock.Mock()
        request.return_value = (mocked_result, mocked_envelope_sent, mocked_envelope_received)
        args = ('arg',)
        kwargs = {'kw': 'kw'}
        expected_request = SoapRequest(
            method_name='methodName',
            args=args,
            kwargs=kwargs)
        expected_response = SoapResponse(
            request=expected_request,
            result=mocked_result,
            envelope_sent=mocked_envelope_sent,
            envelope_received=mocked_envelope_received)

        requestor = SoapRequestor(self.soap_client)
        response = requestor.request('methodName', *args, **kwargs)

        self.assertEqual(expected_response, response)

    def test_request_server_exception(self):
        request = self.soap_client.request
        request.side_effect = SoapServerException('code', 123)

        requestor = SoapRequestor(self.soap_client)
        with self.assertRaises(SoapServerException) as ctx:
            requestor.request('methodName', 'arg', kw='kw')
        self.assertEqual(123, ctx.exception.code)
        self.assertEqual('code', ctx.exception.error)

    def test_request_exception(self):
        request = self.soap_client.request
        request.side_effect = Exception

        requestor = SoapRequestor(self.soap_client)
        with self.assertRaises(Exception):
            requestor.request('methodName', 'arg', kw='kw')

    def assert_equal_response(self, first, second, msg=None):
        self.assertEqual(first.result, second.result, msg)
        self.assertEqual(first.envelope_sent, second.envelope_sent, msg)
        self.assertEqual(first.envelope_received, second.envelope_received, msg)
        self.assertEqual(first.request, second.request, msg)

    def assert_equal_request(self, first, second, msg=None):
        self.assertEqual(first.method_name, second.method_name, msg)
        self.assertEqual(first.args, second.args, msg)
        self.assertEqual(first.kwargs, second.kwargs, msg)


class SoapResponseTest(unittest.TestCase):

    def test_get_item(self):
        request = mock.Mock(spec=SoapRequest)
        key = mock.Mock(spec=str)
        item = mock.Mock()
        result = {key: item}
        response = SoapResponse(request=request, result=result, envelope_received=None, envelope_sent=None)
        self.assertEqual(item, response[key])
