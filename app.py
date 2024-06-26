from io import BytesIO
from flask import Flask, send_file, abort, jsonify, request
from webcam import CV2VideoCapture
import threading
from sensor import Sensor 

app = Flask(__name__)

cv2capture = CV2VideoCapture()
cv2capture.activateCamera()

sensor = Sensor()

threading.Thread(target = sensor.start_sensor, daemon=True,).start()
threading.Thread(target = cv2capture.startStream, daemon=True, args = (sensor.alertDeteksiGagal,)).start()

isInferenceStarted = False
jenisKain = None

@app.route("/")
def home():
    return "Server is ready and up"

@app.route("/status")
def status():
    global isInferenceStarted
    if(sensor.status != "OK"):
        return jsonify({"status":str(sensor.status)})
    
    if(isInferenceStarted):
        if(cv2capture.currentDetectionStatus):
            return jsonify({"status":"Gambar Benar!","data":str({
                "density": cv2capture.density,
                "reconstructionerr": cv2capture.reconsturctionerr,
            })})
        else:
            return jsonify({"status":"Gambar Salah!","data":str({
                "density": cv2capture.density,
                "reconstructionerr": cv2capture.reconsturctionerr,
            })})
    
    return jsonify({"status":"Alat Ready"})
    

@app.route("/statusDeteksi")
def detectionStatus():
    return jsonify({"status":str(cv2capture.currentDetectionStatus)})

@app.route("/statusSensor")
def sensorStatus():
    return jsonify({"status":str(sensor.status)})

@app.route("/start")
def setStart():
    global jenisKain
    global isInferenceStarted
    
    cv2capture.shouldrunInference = True
    sensor.shouldBuzzerOn = True
    jenisKain = request.args.get('jeniskain')
    isInferenceStarted = True
    return jsonify({"status":"ok"})

@app.route("/stop")
def setStop():
    global isInferenceStarted

    cv2capture.shouldrunInference = False
    sensor.shouldBuzzerOn = False
    isInferenceStarted = False
    return jsonify({"status":"ok"})


@app.route("/jenisKain")
def getJenisKain():
    global jenisKain
    return jsonify({"status":"ok", "data":jenisKain})


@app.route('/image')
def image():
    img = cv2capture.currentimage
    if(img == None):
        return abort(404)
    else:
        buffer = BytesIO()
        buffer.write(img)
        buffer.seek(0)
        return send_file(
            buffer,
            mimetype='image/jpeg'
        )

