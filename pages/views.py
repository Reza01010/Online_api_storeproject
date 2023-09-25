from rest_framework.decorators import api_view
from rest_framework.response import Response


@api_view(['GET'])
def home_page_view(request):
    return Response({"message": "welcome home"})
