import pandas as pd
import re
import ast
from datetime import datetime
import pytz
 
filename = "cellphoneS_laptops.csv"
def extract_info(text):
    result = {}
    
    # Regex to match each key-value pair
    pattern = re.compile(r'([\w\s]+):\s*(\[.*?\]|[^,]+)(?=,|$)')
    
    matches = pattern.findall(text)
    for key, value in matches:
        key = key.strip()
        
        # If value looks like a list, parse it as a list
        if value.startswith('[') and value.endswith(']'):
            try:
                value = ast.literal_eval(value)  # Safely parse the list
            except:
                pass  # If parsing fails, keep it as a string
        
        result[key] = value.strip() if isinstance(value, str) else value
    
    return result

def extract_disk_volume(disk):
    if isinstance(disk, list):
        disk = disk[0]
    t = "gb" in disk.lower()
    match = re.search(r'\d+', disk)  # Looks for one or more digits
    if t:
        return int(match.group()) if match else None  
    else:
        return 1024*int(match.group()) if match else None 


def extract_intel_cpu(cpu_string):
    if isinstance(cpu_string, list):
        cpu_string = cpu_string[0]
    pattern = (
        r'(?P<brand>Intel(?:\s+[^\s()]+)*)\s+'               # Match "Intel" followed by series (e.g., Core, Celeron)
        r'(?P<model>[iI]?[3-9]?(?:\s+Ultra|\s+Raptor\s+Lake)?'  # Capture optional "Ultra" or "Raptor Lake" designation
        r'\s*\d{1,2}\s*[-]?\s*\d{3,4}[A-Z]*)'                # Capture model with optional hyphen and suffix letters (e.g., "12450H")
        r'(?:\s*Processor)?'                                  # Optional "Processor" keyword
        r'(?:\s*\d*\.\d*\s*GHz)?'                             # Optional frequency info (e.g., "1.1 GHz")
        r'(?:\s*\(.*?\))?'          
    )
    
    # Search for the pattern in the input string
    match = re.search(pattern, cpu_string)
    
    if match:
        # Extract the brand and model
        brand = match.group('brand').strip().replace('®', '').replace('™', '')
        model = match.group('model').strip().replace('-', ' ')
        
        # Return the formatted output
        return f"{brand} {model}"
    else:
        return cpu_string  # Return original string if no match
    

def extract_mac_cpu(cpu_string):
    # Regular expression to capture the "Apple M[1-3] (Pro|Max)?" pattern
    match = re.search(r"Apple M\d(?: (Pro|Max))?", cpu_string)
    if match:
        return match.group(0)
    return cpu_string  # If no match, return the original text (optional behavior)

def extract_amd_cpu(cpu_string):
    # Regular expression to capture "AMD Ryzen [Series] [Model]" pattern
    match = re.search(r"AMD Ryzen (R\d|[3579])\s*[-]?\s*\d{4}[A-Z]+", cpu_string)
    if match:
        return match.group(0).replace("-", " ").replace(" - ", " ")
    return cpu_string  # If no match, return the original text (optional behavior)

def extract_cpu(cpu):
    if isinstance(cpu, list):
        cpu = cpu[0]
    if "intel" in cpu.lower():
        return extract_intel_cpu(cpu)
    elif "amd" in cpu.lower():
        return extract_amd_cpu(cpu)
    elif "apple" in cpu.lower():
        return extract_mac_cpu(cpu)
    else:
        return -1


def extract_screen_size(screen):
    size = float(re.search(r"\d+(\.\d+)?", screen).group())
    return size

def extract_nvidia_card(card):
    match = re.search(r"(NVIDIA GeForce (RTX|GTX|MX) \d{3,4}(?: Ti)?)", card, re.IGNORECASE)
    return match.group(1).replace("nvidia", "NVIDIA").replace("Nvidia", "NVIDIA").replace("NVidia", "NVIDIA").replace("Geforce", "GeForce").replace("geforce", "GeForce") if match else None


def extract_amd_card(card):
    match = re.search(r"(AMD Radeon(?: RX)?(?: \d{3,4}[A-Z]?)? Graphics|AMD Radeon(?: RX)? \d{3,4}[A-Z]?)", card, re.IGNORECASE)
    return match.group(1).replace("amd", "AMD").replace("radeon", "Radeon") if match else None

def extract_intel_card(card):
    return card.replace("Intel", "INTEL")

def extract_card(card):
    if isinstance(card, list):
        card = card[0]
    if "nvidia" in card.lower():
        return extract_nvidia_card(card)
    elif "amd" in card.lower():
        return extract_amd_card(card)
    elif "intel" in card.lower():
        return extract_intel_card(card)
    else:
        return -1

def extract_ram_volume(ram):
    return float(re.search(r'\d+', ram).group())


def process_each(row):
    laptop = {}
    laptop["Tên máy"]  = row["Title"]
    laptop["Giá"] = row["Price"]
    laptop["Link"] = row["URL"]
    specs = extract_info(row["Specs"])

    for key, value in specs.items():
        if key == "Loại card đồ họa":
            card = extract_card(value)
            if card != -1:
                laptop["Card đồ họa"] = card
        elif key == "Loại CPU":
            cpu = extract_cpu(value)
            laptop["CPU"] = cpu
        elif key == "Dung lượng RAM":
            v = extract_ram_volume(value)
            laptop["Dung lượng RAM (GB)"] = v
        elif key == "Ổ cứng":
            v = extract_disk_volume(value)
            laptop["Dung lượng Ổ cứng (GB)"] = v
        elif key == "Kích thước màn hình":
            size = extract_screen_size(value)
            laptop["Kích thước màn hình (inches)"] = size
        else:
            laptop[f"{key}"] = value
    return laptop

def start_process():
    df = pd.read_csv(filename)
    gmt_plus_7 = pytz.timezone("Asia/Bangkok")  # GMT+7 timezone
    laptops = []
    for index, row in df.iterrows():
        laptop = process_each(row)
        laptop["Time"] =  datetime.now(gmt_plus_7)
        laptop["Website"] = "CellphoneS"
        laptops.append(laptop)
    return laptops
        

    

        







   


