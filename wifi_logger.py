import subprocess
import time
from datetime import datetime

LOG_FILE = "wifi_log.txt"
CHECK_INTERVAL = 1  # секунд

def get_wifi_status():
    try:
        output = subprocess.check_output("netsh wlan show interfaces", shell=True, text=True)
        status = "Unknown"
        ssid = "N/A"
        signal = "N/A"
        for line in output.splitlines():
            if "State" in line:
                status = line.split(":")[1].strip()
            elif "SSID" in line and "BSSID" not in line:
                ssid = line.split(":")[1].strip()
            elif "Signal" in line:
                signal = line.split(":")[1].strip()
        return status, ssid, signal
    except subprocess.CalledProcessError:
        return "Error", "N/A", "N/A"

def check_internet(host="8.8.8.8"):
    try:
        # ping -n 1 для Windows, -c 1 для Linux/macOS
        output = subprocess.check_output(f"ping -n 1 {host}", shell=True, stderr=subprocess.DEVNULL, text=True)
        if "TTL=" in output:
            return True
        else:
            return False
    except subprocess.CalledProcessError:
        return False

def log_status():
    while True:
        status, ssid, signal = get_wifi_status()
        internet = check_internet()
        internet_status = "online" if internet else "offline"
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] Status: {status}, SSID: {ssid}, Signal: {signal}, Internet: {internet_status}"
        print(log_entry)
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log_entry + "\n")
        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    print(f"Старт логгера Wi-Fi с проверкой интернета каждые {CHECK_INTERVAL} секунд.")
    log_status()
