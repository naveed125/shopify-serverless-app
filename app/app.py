from chalice import Chalice, Response
import http.client
import json
import os
import time

app = Chalice(app_name='app')

#
# Step 1: Get Client credentials, see doc here
# https://shopify.dev/tutorials/authenticate-with-oauth#step-1-get-client-credentials
#
@app.route('/')
def index():

    request = app.current_request
    params = request.query_params

    # Debug helper, uncomment the following
    # return request.to_dict()

    if not params:
        return Response(
            body="STATUS OK",
            status_code=200,
            headers={
                'Content-Type': 'text/plain'
            }
        )

    url = request.context.get('path')
    shop = params.get('shop')
    hmac = params.get('hmac')
    timestamp = params.get('timestamp')
    api_key = os.getenv('API_KEY')
    scopes = "read_orders,read_customers"
    redirect_uri = "https://k2jog2foqe.execute-api.us-east-2.amazonaws.com/api/confirm/install"
    nonce = time.time()

    #
    # Step 2: Ask for permission, see doc here
    # https://shopify.dev/tutorials/authenticate-with-oauth#step-2-ask-for-permission
    #
    if hmac and shop:
        url = f"https://{shop}/admin/oauth/authorize?client_id={api_key}&scope={scopes}&redirect_uri={redirect_uri}&state={nonce}"
        return Response(
            status_code=301,
            body='',
            headers={'Location': url}
        )

    body = f"<pre>{request.method}\n url={url}\n shop={shop}\n timestamp={timestamp}\n hmac={hmac}\n</pre>"
    return Response(
        body=body,
        status_code=200,
        headers={
            'Content-Type': 'text/html'
        }
    )

#
# Step 3: Confirm installation, see doc here
# https://shopify.dev/tutorials/authenticate-with-oauth#step-3-confirm-installation
#
@app.route('/confirm/install')
def confirmInstall():

    request = app.current_request
    params = request.query_params

    # debug helper, uncomment the following
    # return request.to_dict()

    if not params:
        return Response(
            body="INVALID REQUEST",
            status_code=500,
            headers={
                'Content-Type': 'text/plain'
            }
        )

    shop = params.get('shop')
    authorization_code = params.get('code')
    hmac = params.get('hmac')
    timestamp = params.get('timestamp')
    state = params.get('state')
    api_key = os.getenv('API_KEY')
    api_secret = os.getenv('API_SECRET')

    # TODO verify hmac

    # Get Access Token by making a post request to Shopify
    conn = http.client.HTTPSConnection(shop)
    conn.request(
        'POST',
        f"https://{shop}/admin/oauth/access_token",
        json.dumps({
            'client_id': api_key,
            'client_secret': api_secret,
            'code': authorization_code
        }),
        {
            'Content-type': 'application/json'
        }
    )

    response = conn.getresponse()
    content = response.read().decode()

    # Response content should look something like this
    # {
    #     "code": "95e04927ddf9cd0b0abb3242de343d5661",
    #     "hmac": "7ab88659c73a72323432b5e7cd011105a977d6af517991cb709c4f00c9c0e0",
    #     "shop": "shopname.myshopify.com",
    #     "state": "1593318793.829355",
    #     "timestamp": "1593318794"
    # }

    if response.status != 200:
        return Response(
            body=content,
            status_code=response.status,
            headers={
                'Content-Type': 'text/plain'
            }
        )

    # In a real app you want to save this token somewhere for making Shopify api calls
    decoded = json.loads(content)
    return Response(
        body=decoded.get('access_token'),
        status_code=response.status,
        headers={
            'Content-Type': 'text/plain'
        }
    )
