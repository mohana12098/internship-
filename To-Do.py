from flask import Flask, request, jsonify
import psycopg2

app =Flask(__name__)

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

def create_To_Do_table():
    connection = get_db_connection()
    cur = connection.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS To_Do_table(
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL UNIQUE,
            description TEXT NOT NULL,
            status TEXT,
            created_at TIMESTAMP(0) WITHOUT TIME ZONE DEFAULT CURRENT_TIMESTAMP
            )
""")
    connection.commit()
    cur.close()
    connection.close()

create_To_Do_table()

@app.route("/send_task", methods = {'POST'})
def send_task():
    title =request.json['title']
    description =request.json['description']
    status =request.json['status']
    connection = get_db_connection()
    cur = connection.cursor()
    cur.execute("""
        INSERT INTO To_Do_table(title,description,status) VALUES(%s,%s,%s)
""",(title,description, status))
    connection.commit()
    cur.close()
    connection.close()
    return jsonify({"message":"task sended successfully"}),201

@app.route("/get_task", methods =['GET'])
def get_task():
    connection =get_db_connection()
    cur =connection.cursor()
    cur.execute("""
        select * from To_Do_table
""")
    Data = cur.fetchall()
    cur.close()
    connection.close()
    results =[]
    for row in Data:
        results.append({
        "id":row[0],
        "title":row[1],
        "description":row[2],
        "status":row[3],
        "created_at":row[4]    
        })
    return jsonify(results),200

@app.route("/update/<int:id>",methods =['PUT'])
def update(id):
    title =request.json['title']
    description =request.json['description']
    status =request.json['status']
    connection =get_db_connection()
    cur= connection.cursor()
    cur.execute("""
        UPDATE To_Do_table SET title=%s,description=%s,status=%s WHERE id=%s
""",(title,description,status,id))
    connection.commit()
    cur.close()
    connection.close()
    return jsonify({"message":"task updated successfully"}),202

@app.route("/delete/<int:id>", methods =['DELETE'])
def delete(id):
    connection =get_db_connection()
    cur =connection.cursor()
    cur.execute("""
        DELETE FROM To_Do_table WHERE id=%s
""",(id,))
    connection.commit()
    cur.close()
    connection.close()
    return jsonify({"message":"task delete successfully"}),203


if __name__== "__main__":
    app.run(debug=True)