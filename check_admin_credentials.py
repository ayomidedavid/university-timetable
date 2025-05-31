import mysql.connector

def check_admin_credentials():
    try:
        # Connect to the database
        connection = mysql.connector.connect(
            host="localhost",
            user="root",
            password="",
            database="university_db"
        )

        cursor = connection.cursor()
        cursor.execute("SELECT * FROM admin;")
        results = cursor.fetchall()

        for row in results:
            print(f"Username: {row[1]}, Password Hash: {row[2]}")  # Assuming username is in column 1 and password hash in column 2

    except mysql.connector.Error as err:
        print(f"Error: {err}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == "__main__":
    check_admin_credentials()
