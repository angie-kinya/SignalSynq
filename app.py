from flask import Flask, render_template, Response
import json
from detector import VehicleDetector, TrafficSignalController

app = Flask(__name__)

# Initialize components
detector = VehicleDetector(model_path="yolov4.weights", config_path="yolov4.cfg")
controller = TrafficSignalController()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    pass

@app.route('/traffic_data')
def traffic_data():
    # Sample data 
    lane_counts = {
        "north": 15,
        "south": 8,
        "east": 20,
        "west": 12
    }
    signal_times = controller.calculate_signal_timing(lane_counts)
    
    return Response(
        json.dumps({
            "lane_counts": lane_counts,
            "signal_times": signal_times,
            "recommendations": {
                lane: controller.get_route_recommendation(lane, lane_counts)
                for lane in lane_counts
            }
        }),
        mimetype='application/json'
    )

if __name__ == '__main__':
    app.run(debug=True)
