import unittest
from unittest.mock import patch
from datetime import datetime
import os

import wifi_logger  # Файл с основным кодом должен быть wifi_logger.py

class TestWifiLogger(unittest.TestCase):
    def setUp(self):
        self.test_time = datetime(2025, 7, 3, 12, 0, 0)
        self.test_entry = "Wi-Fi: connected, SSID: TestSSID, Signal: 99%, Internet: online, Ping: 23 ms"
        self.log_file = wifi_logger.LOG_FILE
        self.excel_file = wifi_logger.EXCEL_FILE

        # Удаляем файлы перед тестом
        for f in [self.log_file, self.excel_file]:
            if os.path.exists(f):
                os.remove(f)

    def tearDown(self):
        # Удаляем файлы после теста
        for f in [self.log_file, self.excel_file]:
            if os.path.exists(f):
                os.remove(f)

    def test_log_to_file_creates_and_logs_entry(self):
        wifi_logger.log_to_file(self.test_entry)
        self.assertTrue(os.path.exists(self.log_file))

        with open(self.log_file, "r", encoding="utf-8") as f:
            content = f.read()
            self.assertIn(self.test_entry, content)

    def test_save_to_excel_creates_file_and_sheet(self):
        wifi_logger.save_to_excel(
            self.test_time,
            "connected",
            "TestSSID",
            99,
            "online",
            23
        )

        self.assertTrue(os.path.exists(self.excel_file))

        from openpyxl import load_workbook
        wb = load_workbook(self.excel_file)
        sheetname = self.test_time.strftime("%d.%m.%y")
        self.assertIn(sheetname, wb.sheetnames)

        ws = wb[sheetname]

        # Проверка данных
        self.assertEqual(ws.cell(row=2, column=2).value, "connected")
        self.assertEqual(ws.cell(row=2, column=3).value, "TestSSID")
        self.assertEqual(ws.cell(row=2, column=4).value, 99)
        self.assertEqual(ws.cell(row=2, column=5).value, "online")
        self.assertEqual(ws.cell(row=2, column=6).value, 23)

        # Проверка, что график создан
        self.assertTrue(ws._charts)

    @patch("wifi_logger.subprocess.check_output")
    def test_get_wifi_status_parsing(self, mock_subprocess):
        mock_subprocess.return_value = (
            "State : connected\n"
            "SSID : TestNet\n"
            "Signal : 75%"
        )
        status, ssid, signal = wifi_logger.get_wifi_status()
        self.assertEqual(status, "connected")
        self.assertEqual(ssid, "TestNet")
        self.assertEqual(signal, 75)

    @patch("wifi_logger.subprocess.check_output")
    def test_ping_latency_success(self, mock_subprocess):
        mock_subprocess.return_value = "Reply from 8.8.8.8: bytes=32 time=42ms TTL=55"
        latency = wifi_logger.ping_latency()
        self.assertEqual(latency, 42)

    @patch("wifi_logger.subprocess.check_output", side_effect=Exception("Timeout"))
    def test_ping_latency_failure(self, mock_subprocess):
        latency = wifi_logger.ping_latency()
        self.assertEqual(latency, -1)

    def test_has_state_changed_true(self):
        wifi_logger.last_state = {
            "wifi_status": "connected",
            "internet_status": "online",
            "signal": 90
        }
        changed = wifi_logger.has_state_changed("disconnected", "offline", 50)
        self.assertTrue(changed)

    def test_has_state_changed_false(self):
        wifi_logger.last_state = {
            "wifi_status": "connected",
            "internet_status": "online",
            "signal": 90
        }
        changed = wifi_logger.has_state_changed("connected", "online", 92)
        self.assertFalse(changed)


if __name__ == "__main__":
    unittest.main(verbosity=2)
