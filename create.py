from flask import Flask, request, jsonify
import psycopg2
from flask_bcrypt import Bcrypt
import jwt
import datetime

app =Flask(__name__)

bcrypt =Bcrypt(app)

#database config
DB_HOST ="localhost"
DB_NAME ="postgres"
DB_USER ="postgres"
DB_PASSWORD ="2612"

def get_db_connection():
    return psycopg2.connect(
        host = DB_HOST,
        database =DB_NAME,
        user =DB_USER,
        password=DB_PASSWORD
    )

#create student table
def create_users_table():
    connection = get_db_connection()
    cur = connection.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users_db(
            user_id SERIAL PRIMARY KEY,
            username TEXT NOT NULL,
            password TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE
        );
    """)
    connection.commit()
    cur.close()
    connection.close()


#create note table
def create_To_Do_table():
    connection =get_db_connection()
    cursor = connection.cursor()
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS To_Do(
                id SERIAL PRIMARY KEY,
                user_id INTEGER REFERENCES users_table(user_id),
                title TEXT NOT NULL UNIQUE,
                description TEXT NOT NULL,
                status TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
    """)
    connection.commit()
    cursor.close()
    connection.close()

create_users_table()
create_To_Do_table()

SECRET_KEY ="this is my key"

def create_jwt(user_id, username):
    payload ={
        "user_id":user_id,
        "username":username,
        "exp": datetime.datetime.utcnow()+datetime.timedelta(minutes=10)
    }
    token =jwt.encode(payload,SECRET_KEY,algorithm="HS256")
    return token

#verify JWT
def verify_jwt(token):
    try:
        data =jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
        return data
    except:
        return None
    
@app.route('/signup',methods=['POST'])
def signup():
    username =request.json['username']
    email =request.json['email']
    password =request.json['password']
    if not username or not email or not password:
        return jsonify({"error":"all fields required"}),400
    hashed_password =bcrypt.generate_password_hash(password).decode("utf-8")
    connection =get_db_connection()
    cur = connection.cursor()
    cur.execute("""
        INSERT INTO users_table(username,email,password)VALUES(%s,%s,%s)
                returning user_id
""",(username,email,hashed_password))
    user_id = cur.fetchone()[0]
    connection.commit()
    cur.close()
    connection.close()
    token =create_jwt(user_id,username)
    return jsonify({"message":"signup successful",
                    "token":token})

@app.route('/login',methods=['POST'])
def login():
    email = request.json['email']
    password =request.json['password']
    if not email or not password:
        return jsonify(({"error":"all fields are required"})),400
    connection =get_db_connection()
    cur =connection.cursor()
    cur.execute("""
            select user_id, username, password from users_table where email=%s
""",(email,))
    user=cur.fetchone()
    connection.commit()
    cur.close()
    connection.close()
    if not user:
        return jsonify({"error":"user not found"})
    user_id, username, hashed_password= user
    if not bcrypt.check_password_hash(hashed_password,password):
        return jsonify({"error":"invalid password"}),401
    token =create_jwt(user_id,username)
    return jsonify({
        "message":"login successful",
        "token":token,
        "user":{
            "user_id":user_id,
            "username":username,
            "email":email
        }
    })


#CREATE NOTE
@app.route("/Create_todo",methods=['POST'])
def Create_todo():
    token = request.headers.get("Authorization")
    if not token:
        return jsonify({"error":"Token required"}),401
    
    user_data =verify_jwt(token)
    if user_data is None:
        return jsonify({"error":"invalid or expired token"}),401
    user_id =user_data["user_id"]
    
    title =request.json['title']
    description =request.json['description']
    if not title or not description:
        return jsonify({"error":"all fields required"}),400
    connection =get_db_connection()
    cursor =connection.cursor()
    cursor.execute("""
        INSERT INTO To_Do(user_id,title,description)VALUES(%s,%s,%s)
""", (user_id,title,description))
    connection.commit()
    cursor.close()
    connection.close()
    return jsonify({
        "message":"Note created successfully",
        "user_id":user_id,
    }),201

@app.route("/get_todo",methods=['GET'])
def get_todo():
    token = request.headers.get("Authorization")
    if not token:
        return jsonify({"error":"Token required"}),401
    user_data =verify_jwt(token)
    if user_data is None:
        return jsonify({"error":"invalid or expired token"}),401
    connection =get_db_connection()
    cur =connection.cursor()
    cur.execute("""
        select id,title,description,created_at from To_Do
                where user_id=%s;
""",(user_data["user_id"],))
    notes =cur.fetchall()
    cur.close()
    connection.close()
    return jsonify({
        "user_id":user_data["user_id"],
        "username":user_data["username"],
        "notes":[{
            "id":note[0],
            "title":note[1],
            "description":note[2],
            "created_at":note[3]
        }
        for note in notes
        ]
    })

@app.route("/update_todo/<int:id>",methods=['PUT'])
def update_todo(id):
    token = request.headers.get("Authorization")
    if not token:
        return jsonify({"error":"Token required"}),401
    user_data =verify_jwt(token)
    if user_data is None:
        return jsonify({"error":"invalid or expired token"}),401
    title =request.json['title']
    description =request.json['description']
    connection =get_db_connection()
    cur =connection.cursor()
    cur.execute("""
        select * from To_Do
                where id=%s and user_id=%s
""",(id,user_data["user_id"]))
    note =cur.fetchone()

    if not note:
        return jsonify({"error":"note not found"}),401
    cur.execute("""
        update To_Do set title =%s,description=%s
                where id=%s;
""",(title,description,id))
    connection.commit()
    cur.close()
    connection.close()
    return jsonify({
        "message":"note updated successfully"
    }),200

@app.route("/delete_todo/<int:id>",methods=['DELETE'])
def delete_todo(id):
    token = request.headers.get("Authorization")
    if not token:
        return jsonify({"error":"Token required"}),401
    user_data =verify_jwt(token)
    if user_data is None:
        return jsonify({"error":"invalid or expired token"}),401
    connection =get_db_connection()
    cur =connection.cursor()
    cur.execute("""
        DELETE FROM To_Do where id=%s
""",(id,))
    connection.commit()
    cur.close()
    connection.close()
    return jsonify({"message":"note delete successfully"}),203
    

if __name__=="__main__":
    app.run(debug=True)
    

