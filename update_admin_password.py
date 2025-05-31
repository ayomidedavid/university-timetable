from flask_mysqldb import MySQL
from werkzeug.security import generate_password_hash
from config import Config
import MySQLdb

# MySQL Configuration
db = MySQLdb.connect(
    host="localhost",
    user="root",
    password="",
    database="university_db"
)

# New password to set
new_password = "12345678"  # Change this to the desired password
hashed_password = generate_password_hash(new_password)

# Update the admin password in the database
cursor = db.cursor()
cursor.execute("UPDATE admin SET password = %s WHERE username = %s", (hashed_password, 'admin'))
db.commit()

print("Admin password updated successfully.")
cursor.close()
db.close()
