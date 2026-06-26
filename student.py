from flask import Flask, request, jsonify
import psycopg2
from flask_bcrypt import Bcrypt

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

# create student table
def create_student_table():
    connection = get_db_connection()
    cur = connection.cursor()
    cur.execute("""
            CREATE TABLE IF NOT EXISTS student_dt(
                id SERIAL PRIMARY KEY,
                studentname TEXT NOT NULL,
                age TEXT NOT NULL,
                course TEXT NOT NULL
                );
""")
    connection.commit()
    cur.close()
    connection.close()

create_student_table()

@app.route("/apply", methods = {'POST'})
def apply():
    studentname =request.json['studentname']
    age =request.json['age']
    course =request.json['course']
    connection = get_db_connection()
    cur = connection.cursor()
    cur.execute("""
        INSERT INTO student_dt(studentname,age,course) VALUES(%s,%s,%s)
""",(studentname,age,course))
    connection.commit()
    cur.close()
    connection.close()
    return jsonify({"message":"student applied successfully"}),201

@app.route("/get_student", methods =['GET'])
def get_student():
    connection =get_db_connection()
    cur =connection.cursor()
    cur.execute("""
        select * from student_dt
""")
    Data = cur.fetchall()
    cur.close()
    connection.close()
    results =[]
    for row in Data:
        results.append({
        "id":row[0],
        "studentname":row[1],
        "age":row[2],
        "course":row[3]
        })
    return jsonify(results),200

@app.route("/update_student/<int:id>",methods =['PUT'])
def update_student(id):
    studentname =request.json['studentname']
    age =request.json['age']
    course =request.json['course']
    connection =get_db_connection()
    cur= connection.cursor()
    cur.execute("""
        UPDATE student_dt SET studentname=%s,age=%s,course=%s WHERE id=%s
""",(studentname,age,course,id))
    connection.commit()
    cur.close()
    connection.close()
    return jsonify({"message":"student updated successfully"}),202

@app.route("/delete_student/<int:id>", methods =['DELETE'])
def delete_student(id):
    connection =get_db_connection()
    cur =connection.cursor()
    cur.execute("""
        DELETE FROM student_dt WHERE id=%s
""",(id,))
    connection.commit()
    cur.close()
    connection.close()
    return jsonify({"message":"student delete successfully"}),203


if __name__== "__main__":
    app.run(debug=True)