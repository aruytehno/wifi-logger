import subprocess
import time
from datetime import datetime

import subprocess
import re
import time
from datetime import datetime

LOG_FILE = "ping_quality_log.txt"
PING_TARGET = "8.8.8.8"
COUNT = 10
THRESHOLD_MS = 500  # выше этого считаем лагом

# LOG_FILE = "wifi_log.txt"
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

def log(entry):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_entry = f"[{timestamp}] {entry}"
    print(full_entry)
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(full_entry + "\n")

def monitor_ping():
    while True:
        try:
            output = subprocess.check_output(f"ping -n {COUNT} {PING_TARGET}", shell=True, text=True)
            lines = output.splitlines()

            for line in lines:
                if "Ответ от" in line or "Reply from" in line:
                    match = re.search(r"time[=<]\s*(\d+)ms", line)
                    if match:
                        latency = int(match.group(1))
                        if latency > THRESHOLD_MS:
                            log(f"⚠️ Высокая задержка: {latency} ms — {line.strip()}")
                elif "Превышен интервал ожидания" in line or "Request timed out" in line:
                    log("❌ Потеря пакета: Request timed out")

            time.sleep(10)

        except KeyboardInterrupt:
            print("Остановлено вручную.")
            break
        except Exception as e:
            log(f"Ошибка: {e}")
            time.sleep(5)

if __name__ == "__main__":
    # print(f"Старт логгера Wi-Fi с проверкой интернета каждые {CHECK_INTERVAL} секунд.")
    # log_status()

    log("🔍 Старт мониторинга пинга к " + PING_TARGET)
    monitor_ping()