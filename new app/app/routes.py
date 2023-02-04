import config as server
import mysql
from flask import request , jsonify , redirect , Response , make_response , json
import requests
import jwt
from main import app
import email_validator


data_base = server.credentials.data_base

def seats(row , column):
    total_seats = {}
    row_number = ord(row) - 64
    total_seat_count = row_number*column
    for i in range (row_number):
        for j in range(1 , (column+1)):
            vertical = chr(64+(i+1))
            horizontal = str(j)
            total = vertical + horizontal
            total_seats[total] = 0

    return total_seats

def admin_login():
    if request.method == 'GET':
        id = request.form['id']
        password = request.form['password']
        cursor = data_base.cursor(dictionary=True)
        cursor.execute(f"SELECT * FROM bookmyshow.admins WHERE id = {id}")
        data_fetched = cursor.fetchone()
        admin_data = {'id' : data_fetched["id"] ,
                      'name' : data_fetched["admin_name"]}
        token_data = {'id' : data_fetched["id"]}
        token = jwt.encode(token_data , app.config['ADMIN_SECRET_KEY'] , algorithm= 'HS256')
        try:
            if data_fetched["password"] == password :
                return jsonify({"status" : "success" , 
                                "code" : "900" , 
                                "token" : token ,
                                "message" : "successfully loged in" ,
                                "data" : admin_data})
        except:
            return 0
        return({"status" : "error" , 
                "code" : "901" , 
                "message" : "invalid id or password" ,
                "data" : None})

def get_users():
    if request.method == 'GET':       
        cursor = data_base.cursor(dictionary=True)
        cursor.execute("SELECT userid,name,emailid FROM bookmyshow.users WHERE status = 1")
        user_data = cursor.fetchall()              
        return jsonify({"status" : "success",
                        "code" : "900" , 
                        "message" : "user details" ,
                        "data":user_data})

def delete_user(id):
    if request.method == 'DELETE':
        cursor = data_base.cursor(dictionary=True)
        cursor.execute(f"UPDATE bookmyshow.users SET status = '0' WHERE (userid = {id})")
        data_base.commit()
        return jsonify({"status" : "success",
                        "code" : "900" , 
                        "message" : "user deleted successfully" ,
                        "data":None})

def get_theaters():
    if request.method == 'GET':
        cursor = data_base.cursor(dictionary=True)
        cursor.execute("SELECT * FROM bookmyshow.theater")
        theater_data = cursor.fetchall()
        return jsonify({"status" : "success",
                        "code" : "900" , 
                        "message" : "list of theaters" ,
                        "data" : theater_data})

def delete_theater(id):
    if request.method == 'DELETE':
        cursor = data_base.cursor(dictionary=True)
        cursor.execute(f"UPDATE bookmyshow.theater SET status = '0' WHERE (theaterid = {id})")
        data_base.commit()
        return jsonify({"status" : "success",
                        "code" : "900" , 
                        "message" : "theater deleted successfully" ,
                        "data":None})


def theater_owner_login():
    if request.method == 'GET':
        theater_id = request.form['id']
        password = request.form['password']
        cursor = data_base.cursor(dictionary=True)
        cursor.execute(f"SELECT theaterid , password , ownername FROM bookmyshow.theaterowners WHERE theaterid = {theater_id}")
        theater_details = cursor.fetchone()
        token_data = {'id' : theater_details['theaterid']}
        token = jwt.encode(token_data , app.config['PARTNER_SECRET_KEY'] , algorithm = 'HS256')        
        try :
            if (password == theater_details['password']):
                return jsonify({"status" : "success" , 
                                "code" : 900 , 
                                "token" : token ,
                                "message" : "successfully loged in" ,
                                "data" : theater_details})
        except:
            return 0
        return({"status" : "error" , 
                "code" : 901 , 
                "message" : "invalid id or password" ,
                "data" : None})

def theater_delete():
    if request.method == 'DELETE':
        cursor = data_base.cursor(dictionary=True)
        token = request.headers['Authorization']
        raw_token = token.split(" ")
        theater_id = jwt.decode(raw_token[1], app.config['PARTNER_SECRET_KEY'] , algorithms='HS256')
        cursor.execute(f"UPDATE bookmyshow.theater SET status = '0' WHERE (theaterid = {theater_id['id']})")
        data_base.commit()
        return jsonify({"status" : "success",
                        "code" : "900" , 
                        "message" : "theater deleted successfully" ,
                        "data":None})

def get_screen_details():    
    if request.method == 'GET':
        cursor = data_base.cursor(dictionary=True)
        token = request.headers['Authorization']
        raw_token = token.split(" ")
        theater_id = jwt.decode(raw_token[1], app.config['PARTNER_SECRET_KEY'] , algorithms='HS256') 
        cursor.execute(f"SELECT * FROM bookmyshow.screens WHERE theaterid = {theater_id['id']}")
        screen_data = cursor.fetchone()
        return jsonify({"status" : "success",
                        "code" : "900" , 
                        "message" : "list of screens" ,
                        "data" : screen_data})

def add_screens():
    if request.method == 'POST':
        new_screen = request.json
        query = "INSERT INTO bookmyshow.screen(screen_id, theaterid, screen_type, seat_vertical, seat_horizontal, total_seats) VALUES ('%s', '%s', '%s', '%s', '%s', '%s')"
        query_val = (new_screen["screen_id"],
                    new_screen["theaterid"],
                    new_screen["screen_type"],
                    new_screen["seat_vertical"],
                    new_screen["seat_horizontal"],
                    new_screen["total_seats"])
        try :
            cursor = data_base.cursor(dictionary=True)
            cursor.execute(query%query_val)
            data_base.commit()
            cursor.close()
            return jsonify({"status" : "success",
                        "code" : "900" , 
                        "message" : "screen added" ,
                        "data":None})
        except :
            return jsonify({"status" : "error",
                            "code" : "902",
                            "message" : "screen already added",
                            "data" : None})
                            
def add_show():
    if request.method == 'POST':
        new_show = request.json
        screen_id = new_show["screenid"]
        cursor = data_base.cursor(dictionary=True)
        cursor.execute(f"SELECT * FROM bookmyshow.screens WHERE screen_id = {screen_id}")
        screen_details = cursor.fetchone()
        cursor.close()
        seat_vertical = screen_details["seat_vertical"]
        seat_horizontal = screen_details["seat_horizontal"]
        total_seats = seats (seat_vertical , seat_horizontal)
        query = "INSERT INTO bookmyshow.showdetails (screenid, moviename, hero, city , showtiming, showdate) VALUES ('%s', '%s', '%s', '%s', '%s', '%s')"
        query_val = (new_show["screenid"],
                     new_show["moviename"],
                     new_show["hero"],
                     new_show["city"],
                     new_show["showtiming"],
                     new_show["showdate"])
        try:                        
            cursor = data_base.cursor(dictionary=True)
            cursor.execute(query%query_val)
            data_base.commit()
            cursor.close()            
            return jsonify({"status" : "success",
                            "code" : "900" , 
                            "message" : "show added" ,
                            "data":None})

        except:
            return jsonify({"status" : "error",
                            "code" : "902" , 
                            "message" : "show not added" ,
                            "data":None})        

def add_movie():
    if request.method == 'POST':
        new_movie = request.json
        movie_name = new_movie['movie_name']
        year = new_movie['year']
        response_API = requests.get(f'http://www.omdbapi.com/?t={movie_name}&y={year}&plot=full&apikey=5e6996f7')
        raw_data = response_API.text
        movie_details = json.loads(raw_data)
        query = "INSERT INTO bookmyshow.moviedetails (imdbid, title, year, releasedate , runtime, genre , director ,actors , imdbrating) VALUES ('%s', '%s', '%s', '%s', '%s', '%s' , '%s' , '%s' , '%s')"
        query_val = (movie_details['imdbID'],
                         movie_details['Title'],
                         movie_details['Year'],
                         movie_details['Released'],
                         movie_details['Runtime'],
                         movie_details['Genre'],
                         movie_details['Director'],
                         movie_details['Actors'],
                         movie_details['imdbRating'],)
        try:            
            cursor = data_base.cursor(dictionary=True)
            cursor.execute(query%query_val)
            data_base.commit()
            cursor.close()
            return jsonify({"status" : "success",
                            "code" : "900" , 
                            "message" : "movie added to the database" ,
                            "data":None})
        except mysql.connector.errors.DataError:
            return jsonify({"status" : "error",
                            "code" : "902" , 
                            "message" : "movie not found" ,
                            "data":None})
        except mysql.connector.errors.IntegrityError:
            return jsonify({"status" : "error",
                            "code" : "902" , 
                            "message" : "movie already added" ,
                            "data":None})

def theater_owner_registration():
    if request.method == 'POST':
        new_theater = request.json
        status = 1
        query="INSERT INTO theaterowners(ownername, email, password) VALUES ('%s','%s','%s')"
        query_val=(new_theater["ownername"],
                   new_theater["emailid"],
                   new_theater["password"])
        cursor = data_base.cursor(dictionary=True)
        cursor.execute(query%query_val)
        data_base.commit()
        cursor.close()
        query="INSERT INTO theater(owner_name, theater_name, address, phone, screens, latitude, longitude, city, status) VALUES ('%s','%s','%s','%s','%s','%s','%s','%s','%s')"
        query_val = (new_theater["ownername"] , 
                     new_theater["theater_name"],
                     new_theater["address"],
                     new_theater["phone"],
                     new_theater["screens"],
                     new_theater["latitude"],
                     new_theater["longitude"],
                     new_theater["city"],
                     status)
        cursor = data_base.cursor(dictionary=True)
        cursor.execute(query%query_val)
        data_base.commit()
        cursor.close()
                
    return jsonify({"status" : "success",
                    "code" : "900" , 
                    "message" : "theater added" ,
                    "data":None})



def user_login():
    if request.method == 'GET':
        id = request.form['id']
        password = request.form['password']
        cursor = data_base.cursor(dictionary=True)
        cursor.execute(f"SELECT * FROM bookmyshow.users WHERE userid = {id}")
        data_fetched = cursor.fetchone()
        user_data = {'id' : data_fetched["userid"] ,
                     'name' : data_fetched["name"]}
        token_data = {'id' : data_fetched["userid"]}
        token = jwt.encode(token_data , app.config['USER_SECRET_KEY'] , algorithm= 'HS256')
        try:
            if data_fetched["password"] == password and data_fetched["status"] == 1 :
                return jsonify({"status" : "success" , 
                                "code" : "900" , 
                                "token" : token ,
                                "message" : "successfully loged in" ,
                                "data" : user_data})
        except:
            return 0
        return({"status" : "error" , 
                "code" : "901" , 
                "message" : "invalid id or password" ,
                "data" : None})


def user_registration():
    if request.method == 'POST':
        new_user = request.json
        query="INSERT INTO users(name , emailid , password) VALUES ('%s','%s','%s')"
        query_val = (new_user["name"],
                     new_user["emailid"],
                     new_user["password"])
        cursor = data_base.cursor(dictionary=True)
        cursor.execute(query%query_val)
        data_base.commit()
        cursor.close()        
    return jsonify({"status" : "success",
                    "code" : "900" , 
                    "message" : "user added" ,
                    "data":None})

def user_delete():
    if request.method == 'DELETE':
        cursor = data_base.cursor(dictionary=True)
        token = request.headers['Authorization']
        raw_token = token.split(" ")
        user_id = jwt.decode(raw_token[1], app.config['USER_SECRET_KEY'] , algorithms='HS256')
        print(user_id)
        cursor.execute(f"UPDATE bookmyshow.users SET status = '0' WHERE (userid = {user_id['id']})")
        data_base.commit()
        return jsonify({"status" : "success",
                        "code" : "900" , 
                        "message" : "user deleted successfully" ,
                        "data":None})


