from chalice import Chalice

app = Chalice(app_name='app')


@app.route('/')
def index():
    return {'status': 'OK'}


