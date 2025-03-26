import cv2
import numpy as np
import os

class VehicleDetector:
    def __init__(self, model_path="yolov4.weights", config_path="yolov4.cfg"):
        if not os.path.isfile(config_path):
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        # Load YOLO Model
        self.net = cv2.dnn.readNet(model_path, config_path)
        self.layer_names = self.net.getLayerNames()
        self.output_layers = [self.layer_names[i-1] for i in self.net.getUnconnectedOutLayers()]
        self.classes = ["car", "truck", "bus", "motorbike"]

    def detect_vehicles(self, img):
        height, width, channels = img.shape

        # Preprocess image for YOLO
        blob = cv2.dnn.blobFromImage(img, 0.00392, (416, 416), (0, 0, 0), True, crop=False)
        self.net.setInput(blob)
        outs = self.net.forward(self.output_layers)

        # Process detections
        class_ids = []
        boxes = []
        confidences = []

        for out in outs:
            for detection in out:
                scores = detection[5:]
                class_id = np.argmax(scores)
                confidence = scores[class_id]
                if confidence > 0.5 and class_id in [2, 5, 7]: # Car, bus, truck classes in COCO dataset
                    center_x = int(detection[0] * width)
                    center_y = int(detection[1] * height)
                    w = int(detection[2] * width)
                    h = int(detection[3] * height)

                    # Rectangle coordinates
                    x = int(center_x - w / 2)
                    y = int(center_y - h / 2)

                    boxes.append([x, y, w, h])
                    confidences.append(float(confidence))
                    class_ids.append(class_id)

        # Apply non-max suppression
        indexes = cv2.dnn.NMSBoxes(boxes, confidences, 0.5, 0.4)

        vehicle_count = len(indexes)
        return vehicle_count, boxes, indexes, class_ids
    
    @staticmethod
    def evaluate_model(detector, test_images, ground_truths):
        """
        Evaluate vehicle detection model
        Args:
            detector: VehicleDetector instance
            test_images: List of test images
            ground_truths: List of ground truth vehicle counts
        Returns:
            Dictionary of evaluation metrics
        """
        true_positives = 0
        false_positives = 0
        false_negatives = 0
        total_vehicles = sum(ground_truths)
        
        for img, gt in zip(test_images, ground_truths):
            count, _, _, _ = detector.detect_vehicles(img)
            if count == gt:
                true_positives += count
            elif count > gt:
                true_positives += gt
                false_positives += (count - gt)
            else:
                true_positives += count
                false_negatives += (gt - count)
        
        precision = true_positives / (true_positives + false_positives)
        recall = true_positives / (true_positives + false_negatives)
        f1_score = 2 * (precision * recall) / (precision + recall)
        
        return {
            "precision": precision,
            "recall": recall,
            "f1_score": f1_score,
            "accuracy": true_positives / total_vehicles
        }
    
class TrafficSignalController:
    def __init__(self):
        self.base_green_time = 30
        self.max_green_time = 60
        self.min_green_time = 10

    def calculate_signal_timing(self, lane_counts):
        """
        Calculate optimal signal timing based on vehicle counts per lane
        Args:
            lane_counts: Dictionary of lane IDs and vehicle counts
        Returns:
            Dictionary of lane IDs and green light durations
        """
        total_vehicles = sum(lane_counts.values())
        if total_vehicles == 0:
            return {lane_id: self.base_green_time for lane_id in lane_counts}
        
        signal_times = {}
        for lane_id, count in lane_counts.items():
            ratio = count / total_vehicles
            green_time = min(
                self.max_green_time,
                max(
                    self.min_green_time,
                    int(self.base_green_time * (1 + ratio))
                )
            )
            signal_times[lane_id] = green_time

        return signal_times
    
    def get_route_recommendation(self, current_lane, lane_counts):
        """
        Suggest alternative routes based on congestion
        Args:
            current_lane: The lane the vehicle is currently in
            lane_counts: Dictionary of lane IDs and vehicle counts
        Returns:
            String recommendation
        """
        sorted_lanes = sorted(lane_counts.items(), key=lambda x: x[1])
        least_congested_lane = sorted_lanes[0][0]
        
        if lane_counts[current_lane] > lane_counts[least_congested_lane] * 1.5:
            return f"Consider switching to {least_congested_lane} for faster route"
        return "Current route is optimal"
