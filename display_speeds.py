# mysql imports
import mysql.connector
from mysql.connector import Error

def fetching_speed_values_from_database():
    speeds = []
    # connecting to the database
    connection = mysql.connector.connect(host="localhost", user="root", password="", database="vehicle_db")
    if connection.is_connected():
        cursor = connection.cursor()

        cursor.execute("SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_schema = 'vehicle_db'")
        vehicle_count = int(int(cursor.fetchone()[0]) / 2)

        for vehicle in range(1, vehicle_count + 1):
            cursor.execute("SELECT * FROM speed_" + str(vehicle))
            myresult = cursor.fetchall()
            speeds.append(myresult[0])

    return speeds