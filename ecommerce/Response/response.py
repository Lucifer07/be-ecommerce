from rest_framework.response import Response as DRFResponse
class Response:
    def __init__(self, status=200, data="", message="", error=""):
        self.status = status
        self.data = data
        self.message = message
        self.error = error
    def Send(self):
        return DRFResponse({
            'data': self.data,
            'message': self.message,
            'error': self.error
        }, status=self.status)