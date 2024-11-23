from datetime import datetime
import requests
from django.conf import settings
from airtable import airtable

def sync_airtable_to_products():
    at = airtable.Airtable(settings.AIRTABLE_BASE_ID, settings.AIRTABLE_TABLE_NAME, api_key=settings.AIRTABLE_API_KEY)
    records = at.get_all()
    return records
def put_products_to_airtable(id,data):
    at = airtable.Airtable(settings.AIRTABLE_BASE_ID, settings.AIRTABLE_TABLE_NAME, api_key=settings.AIRTABLE_API_KEY)
    datas=at.match('id', id)
    dataChange={
        "name":data['name'],
        "price":float(data['price']),
        "stock":data['stock'],
        # "image":img,
        "description":data['description'],
        "updated_at":datetime.now().strftime("%m-%d-%Y")
    }
    if datas:
        at.update(datas['id'], dataChange)
    else:
        at.insert(data)
def delete_products_from_airtable(data):
    at = airtable.Airtable(settings.AIRTABLE_BASE_ID, settings.AIRTABLE_TABLE_NAME, api_key=settings.AIRTABLE_API_KEY)
    data=at.match('id',data.atId)
    if data:
        at.delete(data['id'])
    else:
        return False
def update_stock_to_airtable(id,stock):
    at = airtable.Airtable(settings.AIRTABLE_BASE_ID, settings.AIRTABLE_TABLE_NAME, api_key=settings.AIRTABLE_API_KEY)
    datas=at.match('id', id)
    dataChange={
        "stock":stock,
        "updated_at":datetime.now().strftime("%m-%d-%Y")
    }
    if datas:
        at.update(datas['id'], dataChange)