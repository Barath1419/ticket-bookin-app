from flask import Flask

app = Flask(__name__)

from app import routes


from app import app
from app import routes
from flask import Flask , request , jsonify
from functools import wraps
import jwt


app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
app.config['ADMIN_SECRET_KEY'] = 'i am an admin'
app.config['PARTNER_SECRET_KEY'] = 'i am a partner'
app.config['USER_SECRET_KEY'] = 'i am a user'


def admin_token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization']
            raw_token = token.split(" ")
        if not token:
            return jsonify({"status" : "error" , 
                            "message" : "token missing",
                            "code" : 901 ,
                            "data" : None})
        try:
            token = jwt.decode(raw_token[1], app.config['ADMIN_SECRET_KEY'] , algorithms='HS256')
        except:
            return jsonify({"status" : "error" , 
                            "code" : 902 ,
                            "message" : "invalid token" , 
                            "data" : None})
        return f( *args, **kwargs)
    return decorated

def owner_token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization']
            raw_token = token.split(" ")
        if not token:
            return jsonify({"status" : "error" , 
                            "message" : "token missing",
                            "code" : 901 ,
                            "data" : None})
        try:
            token = jwt.decode(raw_token[1], app.config['PARTNER_SECRET_KEY'] , algorithms='HS256')
        except:
            return jsonify({"status" : "error" , 
                            "code" : 902 ,
                            "message" : "invalid token" , 
                            "data" : None})
        return f( *args, **kwargs)
    return decorated

def user_token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            token = request.headers['Authorization']
            raw_token = token.split(" ")
        if not token:
            return jsonify({"status" : "error" , 
                            "message" : "token missing",
                            "code" : 901 ,
                            "data" : None})
        try:
            token = jwt.decode(raw_token[1], app.config['USER_SECRET_KEY'] , algorithms='HS256')
        except:
            return jsonify({"status" : "error" , 
                            "code" : 902 ,
                            "message" : "invalid token" , 
                            "data" : None})
        return f( *args, **kwargs)
    return decorated

@app.route('/admin/login' , methods = ['GET'])
def admin_login():
    return routes.admin_login()

@app.route('/admin/users' , methods = ['GET'])
@admin_token_required
def users():
    return routes.get_users()

@app.route('/admin/theaters' , methods = ['GET'])
@admin_token_required
def theaters():
    return routes.get_theaters()

@app.route('/admin/users/delete/<int:userid>' , methods = ['DELETE'])
@admin_token_required
def delete_user(userid):
    return routes.delete_user(userid)

@app.route('/admin/theaters/delete/<int:theaterid>' , methods = ['DELETE'])
@admin_token_required
def delete_theater(theaterid):
    return routes.delete_theater(theaterid)



@app.route('/theaterowner/login' , methods = ['GET'])
def theate_rowner_login():
    return routes.theater_owner_login()

@app.route('/theaterowner/screens' , methods = ['GET' , 'POST'])
@owner_token_required
def get_screen_details():
    return routes.get_screen_details()

@app.route('/theaterowner/add_screens' , methods = ['GET','POST'])
@owner_token_required
def add_screens():
    return routes.add_screens()

@app.route('/theaterowner/add_show' , methods = ['GET','POST'])
@owner_token_required
def add_show():
    return routes.add_show()

@app.route('/theaterowner/add_movie' , methods = ['GET','POST'])
@owner_token_required
def add_movie():
    return routes.add_movie()

@app.route('/theaterowner/registration' , methods = ['GET' , 'POST'])
def theater_owner_registration():
    return routes.theater_owner_registration()

@app.route('/theaterowner/delete_account' , methods = ['DELETE'])
@owner_token_required
def theater_delete():
    return routes.theater_delete()


@app.route('/user/login' , methods = ['GET'])
def user_login():
    return routes.user_login()

@app.route('/user/registration' , methods = ['POST'])
def user_registration():
    return routes.user_registration()

@app.route('/user/delete_account' , methods = ['DELETE'])
@user_token_required
def user_delete():
    return routes.user_delete()

if __name__=="__main__":
   app.run(debug=True)


