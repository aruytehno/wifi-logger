import subprocess
import time
import re
from datetime import datetime

LOG_FILE = "wifi_internet_issues_log.txt"
CHECK_INTERVAL = 1  # секунд
PING_TARGET = "8.8.8.8"
PING_TIMEOUT_MS = 1000
THRESHOLD_LATENCY_MS = 500
THRESHOLD_SIGNAL_PERCENT = 30  # Считаем сигнал слабым ниже этого уровня

def get_wifi_status():
    try:
        output = subprocess.check_output("netsh wlan show interfaces", shell=True, text=True)
        status = "Unknown"
        ssid = "N/A"
        signal = -1
        for line in output.splitlines():
            if "State" in line:
                status = line.split(":")[1].strip()
            elif "SSID" in line and "BSSID" not in line:
                ssid = line.split(":")[1].strip()
            elif "Signal" in line:
                signal_str = line.split(":")[1].strip().replace("%", "")
                signal = int(signal_str)
        return status, ssid, signal
    except subprocess.CalledProcessError:
        return "Error", "N/A", -1

def ping_latency(host=PING_TARGET):
    try:
        output = subprocess.check_output(f"ping -n 1 -w {PING_TIMEOUT_MS} {host}", shell=True, text=True)
        if "TTL=" in output:
            match = re.search(r"time[=<]?\s*(\d+)ms", output)
            if match:
                return int(match.group(1))  # задержка в мс
            return 0
        return -1
    except subprocess.CalledProcessError:
        return -1  # означает timeout

def log_to_file(entry):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    full_entry = f"[{timestamp}] {entry}"
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(full_entry + "\n")

def main_loop():
    print("🔍 Старт мониторинга Wi-Fi и интернета...\n")

    while True:
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Получаем Wi-Fi статус
        wifi_status, ssid, signal = get_wifi_status()

        # Получаем задержку пинга
        latency = ping_latency()

        # Определяем статусы
        internet_status = "online" if latency >= 0 else "offline"
        log_line = f"[{timestamp}] Wi-Fi: {wifi_status}, SSID: {ssid}, Signal: {signal}%, Internet: {internet_status}, Ping: {latency if latency >= 0 else 'timeout'} ms"

        # Печатаем всегда
        print(log_line)

        # Логируем в файл, если что-то не так
        if (
            wifi_status.lower() != "connected"
            or signal < THRESHOLD_SIGNAL_PERCENT
            or latency < 0
            or latency > THRESHOLD_LATENCY_MS
        ):
            log_to_file(log_line)

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    try:
        main_loop()
    except KeyboardInterrupt:
        print("\n🛑 Мониторинг остановлен вручную.")
