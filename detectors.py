from ultralytics import YOLO
from PIL import Image
import torch

def load_detector_model(modelname):
    if modelname == "yolov8n.pt":
        yolov8_models_folder = "models/yolov8n.pt"
        model_yolov8 = YOLO(yolov8_models_folder)
        return model_yolov8

def detect(modelname, model, image):
    if modelname == "yolov8n.pt":      
        results = model(image)
        boxes = results[0].boxes
        output = boxes.xyxy
        photo_area = boxes.orig_shape
        true_area = photo_area[0]*photo_area[1]    
        area = get_area(output)
        im_array = results[0].plot()
        img_with_boxes = Image.fromarray(im_array[..., ::-1])
        return img_with_boxes, area, true_area
    
def get_area(output):
    bbox_list = output.cpu().numpy().tolist()
    for bbox in bbox_list:
        x1, y1, x2, y2 = bbox
        width = x2 - x1
        height = y2 - y1
        area = width * height
        total_area =+ area
    return total_area 