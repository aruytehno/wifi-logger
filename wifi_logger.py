import subprocess
import time
from datetime import datetime

LOG_FILE = "wifi_log.txt"
CHECK_INTERVAL = 30  # в секундах

def get_wifi_status():
    try:
        # Получаем вывод команды netsh
        output = subprocess.check_output("netsh wlan show interfaces", shell=True, text=True)
        if "State" in output:
            for line in output.splitlines():
                if "State" in line:
                    state = line.split(":")[1].strip()
                    return state
        return "Unknown"
    except subprocess.CalledProcessError:
        return "Error"

def log_status():
    while True:
        status = get_wifi_status()
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] Wi-Fi status: {status}"
        print(log_entry)

        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(log_entry + "\n")

        time.sleep(CHECK_INTERVAL)

if __name__ == "__main__":
    print(f"Старт логгера Wi-Fi. Проверка каждые {CHECK_INTERVAL} секунд.")
    log_status()
