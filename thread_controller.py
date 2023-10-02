from threading import Thread
from time import sleep
from typing import Optional
from scapy.all import sniff

from Constants import Option, SleepDuration
from Scanner import Scanner
from telegram_api_wrapper.Sender import Sender
from Logger import Logger


def start_sniffer(scanner: Scanner):
	sniffer = Thread(target=sniff, kwargs={"prn": scanner.callback,
	                                   "iface": Option.INTERFACE.value,
	                                   "store": 0})
	sniffer.daemon = True
	sniffer.start()

def start_sec_thread(target, daemon: Optional[bool] = True):
	thread = Thread(target=target)
	thread.daemon = daemon
	thread.start()

def start_all_core_threads(sender: Sender, scanner: Scanner, logger: Logger):
	start_sec_thread(target=scanner.change_channel)
	start_sec_thread(target=logger.schedule_routine)
	start_sec_thread(target=scanner.monitor_cpu_temperature)
	sleep(SleepDuration.INIT_REFRESH_FREQUENCY.value)
	scanner.networks_accumulated = scanner.networks_current.copy()
	start_sec_thread(target=scanner.compare, daemon=False)
