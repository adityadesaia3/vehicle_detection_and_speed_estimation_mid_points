import mysql.connector
from mysql.connector import Error

def estimate_speed(top_left_coordinates_x, top_left_coordinates_y, top_right_coordinates_x, top_right_coordinates_y, bottom_left_coordinates_x, bottom_left_coordinates_y, bottom_right_coordinates_x, bottom_right_coordinates_y, fps_of_video, calibration_distance, traffic_flow):
    
    # calibration details
    top_left = (float(top_left_coordinates_x), float(top_left_coordinates_y))
    top_right = (float(top_right_coordinates_x), float(top_right_coordinates_y))
    bottom_left = (float(bottom_left_coordinates_x), float(bottom_left_coordinates_y))
    bottom_right = (float(bottom_right_coordinates_x), float(bottom_right_coordinates_y))
    distance = float(calibration_distance)

    # Video Details
    frames_per_second = float(fps_of_video)

    try:
        connection = mysql.connector.connect(host='localhost', database='vehicle_db', user='root', password='')
        if connection.is_connected():
            cursor = connection.cursor()
            cursor.execute('select database();')
            record = cursor.fetchone()
            print("Connected to database", record)
            
            print("Estimating the speed of vehicles")
            cursor.execute("SELECT COUNT(*) FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_schema = 'vehicle_db'")
            vehicle_count = int(cursor.fetchone()[0])
            
            for vehicle in range(1, vehicle_count + 1):
                cursor.execute("SELECT * FROM vehicle_" + str(vehicle))
                myresult = cursor.fetchall()
                
                speed = 0		
                frame_count_start = None
                frame_count_end = None
                
                if traffic_flow == "Towards":
                    for each_result in myresult:
                        frame_count = int(each_result[0])
                        b_x = float(each_result[1])
                        b_y = float(each_result[2])
                        
                        if frame_count_start == None:
                            if (b_y > top_left[1]):
                                frame_count_start = frame_count
                                continue
                        
                        if frame_count_start and frame_count_end == None:
                            if (b_y > bottom_left[1]):
                                frame_count_end = frame_count
                        
                        if frame_count_start and frame_count_end:
                            break


                elif traffic_flow == "Away":
                    for each_result in myresult:
                        frame_count = int(each_result[0])
                        b_x = float(each_result[1])
                        b_y = float(each_result[2])

                        if frame_count_start == None:
                            if (b_y < bottom_left[1]):
                                frame_count_start = frame_count
                                continue

                        if frame_count_start and frame_count_end == None:
                            if (b_y < top_left[1]):
                                frame_count_end = frame_count

                        if frame_count_start and frame_count_end:
                            break
                
                try:
                    speed = distance / (abs(frame_count_end - frame_count_start) / frames_per_second)
                    speed = ((speed * 3600)/1000)
                except:
                    speed = "Not Found"

                create_speed_table = "CREATE TABLE speed_" + str(vehicle) + " (speed varchar(32), path_to_image varchar(32))"
                insert_query = "INSERT INTO speed_" + str(vehicle) + " (speed, path_to_image) VALUES ('"+ str(speed)+"', 'static/"+ str(vehicle)+".jpg')"
                cursor.execute(create_speed_table)
                cursor.execute(insert_query)
            
    except Error as e:
        print("Connection error: {}".format(e))
    finally:
        if (connection.is_connected()):
            connection.commit()
            cursor.close()
            connection.close()
            print("Connection closed")  

    

    if traffic_flow == "Away":
        pass
    elif traffic_flow == "Towards":
        pass

    return