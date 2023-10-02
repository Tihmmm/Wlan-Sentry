import subprocess

from pyric.pyw import Card

from Constants import Option, SleepDuration
from Scanner import Scanner
from telegram_api_wrapper.CommanHandler import CommandHandler
from telegram_api_wrapper.Poller import Poller
from telegram_api_wrapper.Sender import Sender
from Logger import Logger
from thread_controller import start_sniffer, start_sec_thread, start_all_core_threads


def main():

    subprocess.call(["airmon-ng", "start", "wlan0"])
    card = Card(p=int(Option.PHINDEX.value), d=Option.INTERFACE.value, i=int(Option.IFINDEX.value))

    sender = Sender()
    scanner = Scanner(sender=sender, card=card)
    logger = Logger(scanner=scanner, sender=sender)
    command_handler = CommandHandler(sender=sender, scanner=scanner, logger=logger)
    poller = Poller(sender=sender, command_handler=command_handler)
    
    start_sniffer(scanner)
    start_sec_thread(target=poller.poll_for_messages)
    start_all_core_threads(sender, scanner, logger)


if __name__ == "__main__":
    main()
