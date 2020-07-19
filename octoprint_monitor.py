from time import sleep
import ujson
import pcd8544
from machine import Pin, SPI
import framebuf as _framebuf
import network
from octoprint_client import OctoPrintClient


def seconds_to_time(seconds: int):
    if seconds is None:
        return "---"
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    if hours == 0 and minutes == 0:
        return "%02d:%02d" % (minutes, seconds)
    return "%02d:%02d" % (hours, minutes)


class OctoPrintMonitor:

    def __init__(self, config_file='_config.json'):
        """
        Load wifi and octoprint configuration from a file
        :param config_file: provide config json file or default is _config.json
        """
        with open(config_file, 'r') as f:
            config = ujson.load(f)
            lcd_config = config.get('lcd_config')
            octoprint_config = config.get('octoprint_config')
            self.octoprint_url = octoprint_config.get('octoprint_base_url')
            self.api_key = octoprint_config['api_key']

            self.lcd_sck = int(lcd_config.get('sck'))
            self.lcd_bl = int(lcd_config.get('bl'))
            self.lcd_cs = int(lcd_config.get('cs'))
            self.lcd_dc = int(lcd_config.get('dc'))
            self.lcd_rst = int(lcd_config.get('rst'))
            self.lsd_miso = int(lcd_config.get('miso'))
            self.lsd_mosi = int(lcd_config.get('mosi'))

            wifi_config = config.get('wifi_config')
            self.wifi_ssid = wifi_config.get('ssid')
            self.wifi_pass = wifi_config.get("wifi_pass")

            self.lcd = None
            self.frame_buff = None
            bl = Pin(27, Pin.OUT, value=1)

            # def init(self) -> None:
            spi = SPI(1)
            spi.init(baudrate=2000000,
                     polarity=0,
                     phase=0,
                     bits=8,
                     firstbit=0,
                     sck=Pin(self.lcd_sck),
                     mosi=Pin(self.lsd_mosi),
                     miso=Pin(self.lsd_miso))

            self.lcd = pcd8544.PCD8544(spi=spi, cs=Pin(self.lcd_cs), dc=Pin(self.lcd_dc), rst=Pin(self.lcd_rst))

            self.buffer = bytearray((pcd8544.HEIGHT // 8) * pcd8544.WIDTH)
            self.frame_buff = _framebuf.FrameBuffer(self.buffer, pcd8544.WIDTH, pcd8544.HEIGHT, _framebuf.MONO_VLSB)

            self.lcd.contrast()
            # self.lcd.data(bytearray(
            #     [0x38, 0x44, 0xFC, 0x4A, 0x4A, 0x4A, 0x34]))

            self.lcd.text(txt='Init...', clear_screen=True)
            wlan_connect = network.WLAN(network.STA_IF)
            wlan_connect.active(True)
            wlan_connect.connect(self.wifi_ssid, self.wifi_pass)

            self.lcd.text('Connecting to ', clear_screen=True)
            self.lcd.text(txt=self.wifi_ssid, y=2)
            while wlan_connect.status() != network.STAT_GOT_IP:
                sleep(1)

            self.lcd.text('Connecting to', clear_screen=True)
            self.lcd.text('OctoPrint', y=2)
            self.octoprint_client = OctoPrintClient(octoprint_url=self.octoprint_url,
                                                    api_key=self.api_key)
            octoprint_version = self.octoprint_client.get_version_info()

            self.lcd.text('Connected:', clear_screen=True)
            self.lcd.text(str(octoprint_version['text']), y=2)

    def show_info(self):
        octoprint_job_info = self.octoprint_client.get_job_info()
        if octoprint_job_info['progress']['printTime'] is None:
            print_time = "-"
        else:
            print_time = seconds_to_time(octoprint_job_info['progress']['printTime'])
        if octoprint_job_info['progress']['printTimeLeft'] is None:
            time_left = "-"
        else:
            time_left = seconds_to_time(octoprint_job_info['progress']['printTimeLeft'])

        self.lcd.text('Print Time', clear_screen=True)
        self.lcd.text(print_time, x=1, y=1)
        self.lcd.text('Time left', y=3)
        self.lcd.text(time_left, x=1, y=4)


# if __name__ == '__main__':
octoprint_monitor = OctoPrintMonitor()
while True:
    octoprint_monitor.show_info()
    sleep(10)
