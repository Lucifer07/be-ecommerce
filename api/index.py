from vercel_wsgi import application

def handler(event, context):
    return application(event, context)
