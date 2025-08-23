
API_KEY = "super-secret-agent-key"

def check_api_key(request):
    provided = request.headers.get("X-API-Key")
    if provided != API_KEY:
        from rest_framework.exceptions import AuthenticationFailed
        raise AuthenticationFailed("Invalid or missing API key")
