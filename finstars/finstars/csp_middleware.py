class CustomCSPMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Добавляем или обновляем заголовок Content-Security-Policy
        response.headers['Content-Security-Policy'] = "script-src 'self' 'unsafe-eval';"

        return response
