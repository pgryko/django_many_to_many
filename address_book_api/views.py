from django.http import HttpResponse
from django.conf import settings

# Create your views here.


def index_html(request):
    """For demo purposes list available urls
    By default django does this when running in dev
    """
    html = """<html><body>
     
    <a href='admin/'>admin/</a></br>
    <a href='api-auth/'>api-auth/</a></br>
    <a href='api/schema/swagger-ui/'>api/schema/swagger-ui/</a></br>
    <a href='api/schema/openapi'>api/schema/openapi</a></br>
    <a href='api/schema/redoc/'>api/schema/redoc/</a></br>
    
     </body></html>"""
    return HttpResponse(html)
