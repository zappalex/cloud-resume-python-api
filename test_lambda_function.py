import unittest
from unittest.mock import MagicMock, patch
from lambda_function import lambda_handler, getVisitorCount, updateVisitorCount, buildResponse

class TestLambdaHandler(unittest.TestCase):

    def test_lambda_handler_health_path(self):
        event = {'httpMethod': 'GET', 'path': '/health'}
        response = lambda_handler(event, None)
        self.assertEqual(response['statusCode'], 200)

    @patch('lambda_function.table')
    def test_lambda_handler_visitor_count_get_path(self, mock_table):
        event = {'httpMethod': 'GET', 'path': '/visitor_count'}
        mock_table.get_item.return_value = {'Item': {'site_name': 'alexashworthdev', 'visitor_count': 42}}
        response = lambda_handler(event, None)
        mock_table.get_item.assert_called_once_with(Key={'site_name': 'alexashworthdev'})
        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(response['body'], '{"site_name": "alexashworthdev", "visitor_count": 42}')

    @patch('lambda_function.table')
    def test_lambda_handler_visitor_count_put_path(self, mock_table):
        event = {'httpMethod': 'PUT', 'path': '/visitor_count'}
        mock_table.update_item.return_value = {'Attributes': {'site_name': 'alexashworthdev', 'visitor_count': 43}}
        response = lambda_handler(event, None)
        mock_table.update_item.assert_called_once_with(
            Key={'site_name': 'alexashworthdev'},
            UpdateExpression='SET visitor_count = visitor_count + :val',
            ExpressionAttributeValues={':val': 1},
            ReturnValues="UPDATED_NEW"
        )
        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(response['body'], '{"Operation": "UPDATE", "Message": "SUCCESS", "UpdatedAttributes": {"Attributes": {"site_name": "alexashworthdev", "visitor_count": 43}}}')

    @patch('lambda_function.table')
    def test_lambda_handler_not_found_path(self, mock_table):
        event = {'httpMethod': 'GET', 'path': '/unknown_path'}
        response = lambda_handler(event, None)
        mock_table.assert_not_called()
        self.assertEqual(response['statusCode'], 404)
        self.assertEqual(response['body'], '"Not Found"')

    @patch('lambda_function.table')
    def test_get_visitor_count_found(self, mock_table):
        mock_table.get_item.return_value = {'Item': {'site_name': 'alexashworthdev', 'visitor_count': 42}}
        response = getVisitorCount('alexashworthdev')
        mock_table.get_item.assert_called_once_with(Key={'site_name': 'alexashworthdev'})
        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(response['body'], '{"site_name": "alexashworthdev", "visitor_count": 42}')

    @patch('lambda_function.table')
    def test_get_visitor_count_not_found(self, mock_table):
        mock_table.get_item.return_value = {}
        response = getVisitorCount('unknown_site')
        mock_table.get_item.assert_called_once_with(Key={'site_name': 'unknown_site'})
        self.assertEqual(response['statusCode'], 404)
        self.assertEqual(response['body'], '{"Message": "site_name: unknown_site not found"}')

    @patch('lambda_function.table')
    def test_get_visitor_count_exception(self, mock_table):
        mock_table.get_item.side_effect = Exception('Some error')
        response = getVisitorCount('alexashworthdev')
        mock_table.get_item.assert_called_once_with(Key={'site_name': 'alexashworthdev'})
        self.assertEqual(response['statusCode'], 500)

    @patch('lambda_function.table')
    def test_update_visitor_count_success(self, mock_table):
        mock_table.update_item.return_value = {'Attributes': {'site_name': 'alexashworthdev', 'visitor_count': 43}}
        response = updateVisitorCount('alexashworthdev')
        mock_table.update_item.assert_called_once_with(
            Key={'site_name': 'alexashworthdev'},
            UpdateExpression='SET visitor_count = visitor_count + :val',
            ExpressionAttributeValues={':val': 1},
            ReturnValues="UPDATED_NEW"
        )
        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(response['body'], '{"Operation": "UPDATE", "Message": "SUCCESS", "UpdatedAttributes": {"Attributes": {"site_name": "alexashworthdev", "visitor_count": 43}}}')

    @patch('lambda_function.table')
    def test_update_visitor_count_exception(self, mock_table):
        mock_table.update_item.side_effect = Exception('Some error')
        response = updateVisitorCount('alexashworthdev')
        mock_table.update_item.assert_called_once_with(
            Key={'site_name': 'alexashworthdev'},
            UpdateExpression='SET visitor_count = visitor_count + :val',
            ExpressionAttributeValues={':val': 1},
            ReturnValues="UPDATED_NEW"
        )
        self.assertEqual(response['statusCode'], 500)

    def test_build_response_no_body(self):
        response = buildResponse(200)
        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(response['headers']['Content-Type'], 'application/json')
        self.assertEqual(response['headers']['Access-Control-Allow-Origin'], '*')
        self.assertNotIn('body', response)

    def test_build_response_with_body(self):
        body_data = {'key': 'value'}
        response = buildResponse(200, body_data)
        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(response['headers']['Content-Type'], 'application/json')
        self.assertEqual(response['headers']['Access-Control-Allow-Origin'], '*')
        self.assertEqual(response['body'], '{"key": "value"}')