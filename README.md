# vehicle_detection_and_speed_estimation_mid_points

1. create "static" folder inside main directory
2. create "videos" folder inside "templates" directory
3. add "yolov3.weight" file inside "yolov3-coco" directory

### to generate PDF
1. download "wkhtmltopdf" and set "wkhtmltopdf/bin path" to environment variables

### to send email
1. add two environment variables to your local machine. EMAIL_ADDRESS and EMAIL_PASSWORD of your gmail account.
2. authorize less secure access

### to run the project
1. download and install XAMPP
2. Start "Apache" and "MySQL" services

# error
[ WARN:0] global C:\Users\appveyor\AppData\Local\Temp\1\pip-req-build-wwma2wne\opencv\modules\dnn\src\dnn.cpp (1429) cv::dnn::dnn4_v20200609::Net::Impl::setUpNet DNN module was not built with CUDA backend; switching to CPU