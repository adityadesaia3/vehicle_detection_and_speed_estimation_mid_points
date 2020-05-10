from flask import Flask, render_template, request, flash, redirect, url_for
import os
from werkzeug.utils import secure_filename

# for YOLOv3 Detection and Speed Estimation
from speed_estimation import estimate_speed
from yolo import yolo_detection

# for assignment of calibration coordinates
from yolo_utils import assign_calibration_coordinates

# for displaying speeds
from display_speeds import fetching_speed_values_from_database

app = Flask(__name__)
app.secret_key = b'qE7psRxhW}QUu\Mb'
filename = ""


# Define the path to the upload folder
dir_path = os.path.dirname(os.path.realpath(__file__))
app.config['UPLOAD_FOLDER'] = dir_path + "/templates/videos/"

# Specifies the maximum size (in bytes) of the files to be uploaded
# app.config['MAX_CONTENT_PATH']


@app.route("/")
def home():
    return render_template("home.html")


# To save uploaded file in folder
@app.route('/video_file_upload', methods = ['GET', 'POST'])
def video_file_upload():
   if request.method == 'POST':
        # check if the post request has the file part
        # if 'file' not in request.files:
        #     flash('No file part')
        #     return redirect(url_for("home"))

        file = request.files['video_file']

        # if file.filename == "":
        #     flash("No selected file")
        #     return redirect(url_for("home"))
        
        if file:
            global filename
            filename = secure_filename(file.filename)
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
            return redirect(url_for("video_file_successfully_uploaded"))


# Display file successfully uploaded message
@app.route("/video_file_successfully_uploaded")
def video_file_successfully_uploaded():
    return render_template("video_file_successfully_uploaded.html")


# Routes page to analyze_video.html page
@app.route("/analyze_video")
def analyze_video():
    return render_template("analyze_video.html")


@app.route("/result_of_analyze", methods=['GET', 'POST'])
def result_of_analyze():
    # Get all the values
    top_left_coordinates_x = request.form["top_left_coordinates_x"]
    top_left_coordinates_y = request.form["top_left_coordinates_y"]

    top_right_coordinates_x = request.form["top_right_coordinates_x"]
    top_right_coordinates_y = request.form["top_right_coordinates_y"]

    bottom_left_coordinates_x = request.form["bottom_left_coordinates_x"]
    bottom_left_coordinates_y = request.form["bottom_left_coordinates_y"]

    bottom_right_coordinates_x = request.form["bottom_right_coordinates_x"]
    bottom_right_coordinates_y = request.form["bottom_right_coordinates_y"]

    fps_of_video = request.form["fps_of_video"]
    calibration_distance = request.form["calibration_distance"]
    traffic_flow = request.form["traffic_flow"]
    
    # estimate_speed( top_left_coordinates_x, top_left_coordinates_y, top_right_coordinates_x, top_right_coordinates_y,
    #                 bottom_left_coordinates_x, bottom_left_coordinates_y, bottom_right_coordinates_x, bottom_right_coordinates_y, 
    #                 fps_of_video, calibration_distance, traffic_flow)

    # return render_template("show_calibration_details.html", top_left_coordinates_x=top_left_coordinates_x, top_left_coordinates_y=top_left_coordinates_y, 
    #                         top_right_coordinates_x=top_right_coordinates_x, top_right_coordinates_y=top_right_coordinates_y,
    #                         bottom_left_coordinates_x=bottom_left_coordinates_x, bottom_left_coordinates_y=bottom_left_coordinates_y,
    #                         bottom_right_coordinates_x=bottom_left_coordinates_x, bottom_right_coordinates_y=bottom_right_coordinates_y,
    #                         fps_of_video=fps_of_video, calibration_distance=calibration_distance, traffic_flow=traffic_flow)


    # assignment of calibration coordinates in yolo_utils
    assign_calibration_coordinates( top_left_coordinates_x, top_left_coordinates_y, top_right_coordinates_x, top_right_coordinates_y,
                                    bottom_left_coordinates_x, bottom_left_coordinates_y, bottom_right_coordinates_x, bottom_right_coordinates_y)

    # yolo_detection and tracking of vehicle
    yolo_detection( filename, fps_of_video)

    # Estimating the speed of the vehicle
    estimate_speed( top_left_coordinates_x, top_left_coordinates_y, top_right_coordinates_x, top_right_coordinates_y,
                    bottom_left_coordinates_x, bottom_left_coordinates_y, bottom_right_coordinates_x, bottom_right_coordinates_y, 
                    fps_of_video, calibration_distance, traffic_flow)

    return redirect(url_for("display"))


@app.route("/display", methods=['GET', 'POST'])
def display():
    speeds = fetching_speed_values_from_database()
    return render_template("display.html", speeds=speeds)

if __name__ == "__main__":
    app.run(debug=True)