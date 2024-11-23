import os
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.conf import settings
from rest_framework.decorators import action
from airtable import airtable
class AirTable(APIView):
    @action(detail=False, methods=['get'])
    def get(self, request):
        at = airtable.Airtable(settings.AIRTABLE_BASE_ID, settings.AIRTABLE_TABLE_NAME, api_key=settings.AIRTABLE_API_KEY)
        records = at.get_all()
        return Response(records, status=status.HTTP_200_OK)