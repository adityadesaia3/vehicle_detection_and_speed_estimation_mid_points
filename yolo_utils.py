import numpy as np
import argparse
import cv2 as cv
import subprocess
import time
import os
import mysql.connector
from mysql.connector import Error
import math
import sys

from PIL import Image

# to see whether the point is inside the quadrilateral or not
from matplotlib import path

connection = None
cursor = None
frame_1 = 0
frame_2 = 0
#Assume
distance = 10
flag1 = True
flag2 = True

count = 1
count_cropped = 1
new_img = 0
set_of_vehicles = set()

top_left_coordinates_x = None
top_left_coordinates_y = None

top_right_coordinates_x = None
top_right_coordinates_y = None

bottom_left_coordinates_x = None
bottom_left_coordinates_y = None

bottom_right_coordinates_x = None
bottom_right_coordinates_y = None


def perpendicular_distance_from_first_line(x, y):
    global top_left_coordinates_x, top_left_coordinates_y, top_right_coordinates_x, top_right_coordinates_y


    m = (top_left_coordinates_y - top_right_coordinates_y) / (top_left_coordinates_x - top_right_coordinates_x)

    numerator = abs(m * x - y + top_left_coordinates_y - m * top_left_coordinates_x)
    denominator = math.sqrt(m*m + 1)

    return numerator / denominator


def perpendicular_distance_from_second_line(x, y):
    global bottom_left_coordinates_x, bottom_left_coordinates_y, bottom_right_coordinates_x, bottom_right_coordinates_y


    m = (bottom_left_coordinates_y - bottom_right_coordinates_y) / (bottom_left_coordinates_x - bottom_right_coordinates_x)

    numerator = abs(m * x - y + bottom_left_coordinates_y - m * bottom_left_coordinates_x)
    denominator = math.sqrt(m*m + 1)

    return numerator / denominator


def assign_calibration_coordinates(t_l_x, t_l_y, t_r_x, t_r_y, b_l_x, b_l_y, b_r_x, b_r_y):
    global top_left_coordinates_x
    global top_left_coordinates_y

    global top_right_coordinates_x
    global top_right_coordinates_y

    global bottom_left_coordinates_x
    global bottom_left_coordinates_y

    global bottom_right_coordinates_x
    global bottom_right_coordinates_y

    top_left_coordinates_x = float(t_l_x)
    top_left_coordinates_y = float(t_l_y)

    top_right_coordinates_x = float(t_r_x)
    top_right_coordinates_y = float(t_r_y)

    bottom_left_coordinates_x = float(b_l_x)
    bottom_left_coordinates_y = float(b_l_y)

    bottom_right_coordinates_x = float(b_r_x)
    bottom_right_coordinates_y = float(b_r_y)


def show_image(img):
    cv.imshow("Image", img)
    cv.waitKey(0)


def is_point_inside(bottom_mid_point):
    global top_left_coordinates_x, top_left_coordinates_y, top_right_coordinates_x, top_right_coordinates_y
    global bottom_left_coordinates_x, bottom_left_coordinates_y, bottom_right_coordinates_x, bottom_right_coordinates_y

    x = bottom_mid_point[0]
    y = bottom_mid_point[1]

    # Himanshu's idea --> to find whether a point is inside a quadrilateral or not
    # x1 = bottom_left_coordinates_x, y1 = bottom_left_coordinates_y
    # x2 = bottom_right_coordinates_x, y2 = bottom_right_coordinates_y
    # x3 = top_right_coordinates_x, y3 = top_right_coordinates_y
    # x4 = top_left_coordinates_x, y4 = top_left_coordinates_y

    # m1 = (y1 - y4) / (x1 - x4)
    # m2 = (y2 - y3) / (x2 - x3)

    # if  ((y < m1 * (x - x1)) and
    #     (y < m2 * (x - x2)) and
    #     (y - y3) and
    #     (y)):
    #     print(True)

    # verts = [
    # (0., 0.),  # left, bottom
    # (0., 1.),  # left, top
    # (1., 1.),  # right, top
    # (1., 0.),  # right, bottom
    # (0., 0.),  # ignored
    # ]

    # to find whether a point is inside a quadrilateral or not
    # origin is at top left corner
    p = path.Path   ([  
                        (top_left_coordinates_x, top_left_coordinates_y),           # left, top
                        (bottom_left_coordinates_x, bottom_left_coordinates_y),     # left, bottom
                        (bottom_right_coordinates_x, bottom_right_coordinates_y),   # right, bottom
                        (top_right_coordinates_x, top_right_coordinates_y)          # right, top
                    ])
    print(f"Origin is at top Contains point: {p.contains_points([(x, y)])[0]}")
    return p.contains_points([(x, y)])[0]

    # to find whether a point is inside a quadrilateral or not
    # origin is at bottom left corner
    # p = path.Path   ([  
    #                     (bottom_left_coordinates_x, bottom_left_coordinates_y),     # left, bottom
    #                     (top_left_coordinates_x, top_right_coordinates_x),          # left, top
    #                     (top_right_coordinates_x, top_right_coordinates_y),         # right, top
    #                     (bottom_right_coordinates_x, bottom_right_coordinates_y)    # right, bottom
    #                 ])
    # print(f"Origin is at bottom Contains point: {p.contains_points([(x, y)])[0]}")

    # p = path.Path([(top_left_coordinates_x, top_left_coordinates_y), (top_right_coordinates_x, top_right_coordinates_y), (bottom_left_coordinates_x, bottom_left_coordinates_y), (bottom_right_coordinates_x, bottom_right_coordinates_y)])
    # return p.contains_points([(x, y)])[0]
    
    # if top_left_coordinates_x <= x <= top_right_coordinates_x or bottom_left_coordinates_x <= x <= bottom_right_coordinates_x:
    #     if top_left_coordinates_y <= y <= bottom_left_coordinates_y or top_right_coordinates_y <= y <= bottom_right_coordinates_y:
    #         print(True)
    #         return True
    # else:
    #     print(False)
    #     return False


def draw_labels_and_boxes(img, boxes, confidences, classids, idxs, colors, labels):
    # If there are any detections
    global count_cropped
    global new_img
    global count
    global flag1
    global flag2
    global frame_1
    global frame_2
    global connection
    global cursor
    global distance
    global set_of_vehicles

    if len(idxs) > 0:
        count += 1
        for i in idxs.flatten():
            # Get the bounding box coordinates
            x, y = boxes[i][0], boxes[i][1]
            w, h = boxes[i][2], boxes[i][3]
            
            # Get the unique color for this class
            color = [int(c) for c in colors[classids[i]]] 

            #manual color
            color = int(1001)       
        
            top_left = (x, y)
            top_right = (x + w, y)
            bottom_right = (x+w, y+h)
            bottom_left = (x, y + h)

            distance_between_top_left_bottom_right = math.sqrt(pow((top_left[0] - bottom_right[0]), 2) + pow((top_left[1] - bottom_right[1]), 2))
            distance_x = abs(bottom_right[0] - bottom_left[0])
            distance_y = abs(top_left[1] - bottom_left[1])

            mid_point = (x + w/2, y + h/2)

            bottom_mid_point = (x + w/2, y + h)
            text = None

            pd_first_line = perpendicular_distance_from_first_line(bottom_mid_point[0], bottom_mid_point[1])
            pd_second_line = perpendicular_distance_from_second_line(bottom_mid_point[0], bottom_mid_point[1])

            is_close_to_first_line = False
            is_close_to_second_line = False
            if pd_first_line < pd_second_line: is_close_to_first_line = True
            else: is_close_to_second_line = True

            # Check if bottom mid point is inside the calibrated lines
            if (is_point_inside(bottom_mid_point)):

                # car = 2
                # truck = 7
                # bus = 5
                if (classids[i] == 2 or classids[i] == 7 or classids[i] == 5) and distance_x > 50 and distance_y > 50:
                    # Crop boxed image
                    cropped_img = new_img.crop((x, y, x+w, y+h))
                    # Save that image temporarily
                    cropped_img.save("temp_img.jpg")


                    is_new_vehicle = None
                    vehicle_number = None
                    if len(set_of_vehicles) > 0:
                        is_new_vehicle = False
                        minimum_distance = float("inf")


                        t_connection = mysql.connector.connect(host="localhost", user="root", password="", database="vehicle_db")
                        t_cursor = None
                        try:
                            if t_connection.is_connected():
                                t_cursor = t_connection.cursor()
                            
                            for current_vehicle in set_of_vehicles:
                                x_last_current_vehicle = None
                                y_last_current_vehicle = None
                                myresult = None

                                #print(current_vehicle)
                                
                                # fetch the last x and y coordinate of "current_vehicle" from the database
                                try:
                                    # check spaces in sql syntax 
                                    # error might occur due to it
                                    t_cursor.execute("SELECT * FROM vehicle_" + str(current_vehicle) + " order by frame_count desc limit 1")
                                    myresult = t_cursor.fetchone()
                                    #print(myresult)
                                except mysql.connector.Error as error:
                                    print(error)
                                    
                                    
                                x_last_current_vehicle = float(myresult[1])
                                y_last_current_vehicle = float(myresult[2])
                                #print(x_last_current_vehicle, y_last_current_vehicle)
                                

                                # find distance between "bottom_mid_point"
                                # and fetched x and y coordinate
                                distance_between_two_points = math.sqrt(pow((x_last_current_vehicle - bottom_mid_point[0]), 2) + pow((y_last_current_vehicle - bottom_mid_point[1]), 2))

                                # if the computed distance is less than minimum distance
                                # replace it with minimum distance
                                # and also store the vehicle_number
                                if minimum_distance > distance_between_two_points:
                                    minimum_distance = distance_between_two_points
                                    vehicle_number = current_vehicle
                        except:
                            print("Unexpected error:", sys.exc_info()[0])
                        finally:
                            t_cursor.close()
                            t_connection.close()

                        perpendicular_distance = perpendicular_distance_from_first_line(bottom_mid_point[0], bottom_mid_point[1])
                        print(f"Perpendicular distance: {perpendicular_distance}\tMinimum Distance: {minimum_distance}")
                        if perpendicular_distance < minimum_distance:
                            is_new_vehicle = True
                    else:
                        is_new_vehicle = True
                    
                    print(set_of_vehicles)

                    if is_new_vehicle:
                        # new vehicle
                        set_of_vehicles.add(count_cropped)
                        cropped_img.save("static/" + str(count_cropped) + ".jpg")

                        # create table
                        create_table_query = "create table vehicle_" + str(count_cropped) + " (frame_count integer, b_x varchar(8), b_y varchar(8), end varchar(1));";
                        
                        # Add the coordinate of the line into the table
                        insert_query = "INSERT INTO vehicle_"+ str(count_cropped) +" (frame_count, b_x, b_y, end) VALUES ("+ str(count) +", "+ str(bottom_mid_point[0]) + ", " + str(bottom_mid_point[1]) + ", " + str(0) + ");"
                        try:
                            result = cursor.execute(create_table_query)
                            result = cursor.execute(insert_query)
                        except mysql.connector.Error as error:
                            print(error)
                        finally:
                            connection.commit()

                        count_cropped += 1
                    else:
                        # do this
                        print(f"new vehicle = False Vehicle number: {vehicle_number}")
                        cropped_img.save("static/" + str(vehicle_number) + ".jpg")

                        # Add the coordinate of the line into the table
                        insert_query = "INSERT INTO vehicle_"+ str(vehicle_number) +" (frame_count, b_x, b_y, end) VALUES ("+ str(count) +", "+ str(bottom_mid_point[0]) + ", " + str(bottom_mid_point[1]) + ", " + str(0) + ");"
                        try:
                            result = cursor.execute(insert_query)
                        except mysql.connector.Error as error:
                            print(error)
                        finally:
                            connection.commit()
                    
                    # Draw the bounding box rectangle and label on the image
                    cv.rectangle(img, (x, y), (x+w, y+h), color, 6)
                    #print("classid {} i = {}".format(classids[i], i))
                    text = "{}: {}".format(labels[classids[i]], vehicle_number)
                    cv.putText(img, text, (x, y-5), cv.FONT_HERSHEY_SIMPLEX, 1, color, 2)

                    print("{}\tTopL = {},\tBottomR = {},\tMid = {},\tBottom_Mid = {},\tName = {}".format(count, top_left, bottom_right, mid_point, bottom_mid_point, text))
                else:
                    text = "{}: {:4f}".format(labels[classids[i]], confidences[i])
                    print("{}\tTopL = {},\tBottomR = {},\tMid = {},\tBottom_Mid = {},\tName = {} Not Considered".format(count, top_left, bottom_right, mid_point, bottom_mid_point, text))
            elif (is_close_to_first_line):
                pass
            elif (is_close_to_second_line):
                
                if (classids[i] == 2 or classids[i] == 7 or classids[i] == 5) and distance_x > 50 and distance_y > 50:

                    # Crop boxed image
                    cropped_img = new_img.crop((x, y, x+w, y+h))
                    # Save that image temporarily
                    cropped_img.save("temp_img.jpg")

                    vehicle_number = None
                    if len(set_of_vehicles) > 0:
                        is_new_vehicle = False
                        minimum_distance = float("inf")

                        t_connection = mysql.connector.connect(host="localhost", user="root", password="", database="vehicle_db")
                        t_cursor = None
                        try:
                            if t_connection.is_connected():
                                t_cursor = t_connection.cursor()
                            
                            for current_vehicle in set_of_vehicles:
                                x_last_current_vehicle = None
                                y_last_current_vehicle = None
                                myresult = None

                                #print(current_vehicle)
                                
                                # fetch the last x and y coordinate of "current_vehicle" from the database
                                try:
                                    # check spaces in sql syntax 
                                    # error might occur due to it
                                    t_cursor.execute("SELECT * FROM vehicle_" + str(current_vehicle) + " order by frame_count desc limit 1")
                                    myresult = t_cursor.fetchone()
                                    #print(myresult)
                                except mysql.connector.Error as error:
                                    print(error)
                                    
                                x_last_current_vehicle = float(myresult[1])
                                y_last_current_vehicle = float(myresult[2])
                                #print(x_last_current_vehicle, y_last_current_vehicle)
                                

                                # find distance between "bottom_mid_point"
                                # and fetched x and y coordinate
                                distance_between_two_points = math.sqrt(pow((x_last_current_vehicle - bottom_mid_point[0]), 2) + pow((y_last_current_vehicle - bottom_mid_point[1]), 2))

                                # if the computed distance is less than minimum distance
                                # replace it with minimum distance
                                # and also store the vehicle_number
                                if minimum_distance > distance_between_two_points:
                                    minimum_distance = distance_between_two_points
                                    vehicle_number = current_vehicle

                            perpendicular_distance = perpendicular_distance_from_second_line(bottom_mid_point[0], bottom_mid_point[1])
                            print(f"Perpendicular distance: {perpendicular_distance}\tMinimum Distance: {minimum_distance}")
                            if minimum_distance > 150 or perpendicular_distance > minimum_distance:
                                vehicle_number = None
                        except:
                            print("Unexpected error:", sys.exc_info()[0])
                        finally:
                            if t_cursor:
                                t_cursor.close()
                            t_connection.close()
                        
                        if vehicle_number:
                            set_of_vehicles.remove(vehicle_number)
                            print(f"end vehicle {vehicle_number}")
                            cropped_img.save("static/" + str(vehicle_number) + ".jpg")

                            # Add the coordinate of the line into the table
                            insert_query = "INSERT INTO vehicle_"+ str(vehicle_number) +" (frame_count, b_x, b_y, end) VALUES ("+ str(count) +", "+ str(bottom_mid_point[0]) + ", " + str(bottom_mid_point[1]) + ", " + str(1) + ");"
                            try:
                                result = cursor.execute(insert_query)
                            except mysql.connector.Error as error:
                                print(error)
                            finally:
                                connection.commit()

                text = "{}: {:4f}".format(labels[classids[i]], confidences[i])
                print("{}\tTopL = {},\tBottomR = {},\tMid = {},\tBottom_Mid = {},\tName = {} Outside".format(count, top_left, bottom_right, mid_point, bottom_mid_point, text))


            
            
            

    return img


def generate_boxes_confidences_classids(outs, height, width, tconf):
    boxes = []
    confidences = []
    classids = []

    for out in outs:
        for detection in out:

            # Get the scores, classid, and the confidence of the prediction
            scores = detection[5:]
            classid = np.argmax(scores)
            confidence = scores[classid]
            
            # Consider only the predictions that are above a certain confidence level
            if confidence > tconf:
                # TODO Check detection
                box = detection[0:4] * np.array([width, height, width, height])
                centerX, centerY, bwidth, bheight = box.astype('int')

                # Using the center x, y coordinates to derive the top
                # and the left corner of the bounding box
                x = int(centerX - (bwidth / 2))
                y = int(centerY - (bheight / 2))

                #print(x, y, scores, classid, confidence, centerX, centerY, bwidth, bheight)

                # Append to list
                boxes.append([x, y, int(bwidth), int(bheight)])
                confidences.append(float(confidence))
                classids.append(classid)

    return boxes, confidences, classids


def infer_image(net, layer_names, height, width, img, colors, labels, connection_db, cursor_db, FLAGS, 
            boxes=None, confidences=None, classids=None, idxs=None, infer=True):
    global new_img 
    global connection
    global cursor
    connection = connection_db
    cursor = cursor_db
    new_img = Image.fromarray(img)

    if infer:
        # Contructing a blob from the input image
        blob = cv.dnn.blobFromImage(img, 1 / 255.0, (416, 416), 
                        swapRB=True, crop=False)

        # Perform a forward pass of the YOLO object detector
        net.setInput(blob)

        # Getting the outputs from the output layers
        start = time.time()
        outs = net.forward(layer_names)
        end = time.time()

        if FLAGS.show_time:
            print ("[INFO] YOLOv3 took {:6f} seconds".format(end - start))

        
        # Generate the boxes, confidences, and classIDs
        boxes, confidences, classids = generate_boxes_confidences_classids(outs, height, width, FLAGS.confidence)
        
        # Apply Non-Maxima Suppression to suppress overlapping bounding boxes
        idxs = cv.dnn.NMSBoxes(boxes, confidences, FLAGS.confidence, FLAGS.threshold)

    if boxes is None or confidences is None or idxs is None or classids is None:
        raise '[ERROR] Required variables are set to None before drawing boxes on images.'
        
    # Draw labels and boxes on the image
    img = draw_labels_and_boxes(img, boxes, confidences, classids, idxs, colors, labels)

    return img, boxes, confidences, classids, idxs
