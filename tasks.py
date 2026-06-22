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

def create_tasks():
    connection = get_db_connection()
    cur = connection.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS tasks(
            id SERIAL PRIMARY KEY,
            title VARCHAR(255) NOT NULL,
            description TEXT,
            status VARCHAR(20) DEFAULT 'pending',
            created_at TIMESTAMP(0) DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP(0) DEFAULT CURRENT_TIMESTAMP
            )
""")
    connection.commit()
    cur.close()
    connection.close()

create_tasks()

@app.route("/send_tasks", methods = {'POST'})
def send_tasks():
    title =request.json['title']
    description =request.json['description']
    status =request.json['status']
    connection = get_db_connection()
    cur = connection.cursor()
    cur.execute("""
        INSERT INTO tasks(title,description,status) VALUES(%s,%s,%s)
""",(title,description, status))
    connection.commit()
    cur.close()
    connection.close()
    return jsonify({"message":"task sended successfully"}),201

@app.route("/get_tasks", methods =['GET'])
def get_tasks():
    connection =get_db_connection()
    cur =connection.cursor()
    cur.execute("""
        select * from tasks
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
        "created_at":row[4],
        "updated_at":row[5]  
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
        UPDATE tasks SET title=%s,description=%s,status=%s,updated_at=CURRENT_TIMESTAMP WHERE id=%s
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
        DELETE FROM tasks WHERE id=%s
""",(id,))
    connection.commit()
    cur.close()
    connection.close()
    return jsonify({"message":"task delete successfully"}),203


if __name__== "__main__":
    app.run(debug=True)
