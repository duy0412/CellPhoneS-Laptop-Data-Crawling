import json
from datetime import datetime
import pytz

def process_each(d):
    laptop = {}
    for key, item in d.items():
        if key == "Product name":
           laptop["Tên máy"] = item
        elif key == "Price":
            laptop["Giá"] = item
        elif key == "CPU Model":
            laptop["CPU"] = item
        elif key == "GPU":
            laptop["Card đồ họa"] = item
        elif key == "RAM size":
            laptop["Dung lượng RAM (GB)"] = item
        elif key == "Storage":
            laptop["Dung lượng ổ cứng (GB)"] = item
        elif key == "Screen size":
            laptop["Kích thước màn hình (inches)"] = item
        else:
            if item != None:
                laptop[f"{key}"] = item
    return laptop


def process_all():
    laptops = []
    gmt_plus_7 = pytz.timezone("Asia/Bangkok")  # GMT+7 timezone
    with open("clean_laptop.json", "r+") as f:
        data = json.load(f)
        for d in data:
            laptop = process_each(d)
            laptop["Time"] =  datetime.now(gmt_plus_7)
            laptop["Website"] = "Phong Vu Laptop"
            laptops.append(laptop)
    return laptops


