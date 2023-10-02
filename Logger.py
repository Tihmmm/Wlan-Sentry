import os
import shutil
from datetime import datetime
from glob import glob
from time import sleep

import schedule
from retry import retry

from Constants import BotChat, BotResponseMessage, Option, SleepDuration
from Scanner import Scanner
from telegram_api_wrapper.Sender import Sender
from utils import format_dataframe, create_text_file


class Logger:

    def __init__(self, scanner: Scanner, sender: Sender):
        self.scanner = scanner
        self.sender = sender

    @staticmethod
    def clear_logs() -> str:
        try:
            log_files = glob(f"{Option.LOGS_DIR_NAME.value}/*")
            for log_file in log_files:
                os.remove(log_file)
            if not os.listdir(Option.LOGS_DIR_NAME.value):
                status = Option.GENERIC_SUCCESS.value
            else:
                status = BotResponseMessage.GENERIC_FAIL.value

        except FileNotFoundError as e:
            status = str(e)

        return status

    @staticmethod
    def create_logs_archive() -> str:
        log_archive_name = f"{datetime.now().strftime('%d-%m')}"
        shutil.make_archive(base_name=log_archive_name, format="zip", root_dir=Option.LOGS_DIR_PATH.value)
        log_archive_path = f"{Option.ROOT_DIR.value}/{log_archive_name}.zip"
        return log_archive_path

    @staticmethod
    def remove_archive(archive_path: str):
        if os.path.isfile(archive_path):
            os.remove(archive_path)

    def hourly_log(self):
        log_fp = f"{Option.LOGS_DIR_NAME.value}/{datetime.now().strftime('%d-%m-%Y_%H:%M')}.log"
        with open(log_fp, "w+") as logf:
            logf.write(self.scanner.networks_current.to_string())

    def daily_log(self):
        self.scanner.logger_working = True
        send_status_ok = False
        exception = ""
        networks_accumulated_file_path = f"{Option.LOGS_DIR_PATH.value}/{Option.NETWORKS_ACCUMULATED_FILE_NAME.value}.txt"
        networks_accumulated = format_dataframe(self.scanner.networks_accumulated, header="BSSID")
        create_text_file(path=networks_accumulated_file_path, content=networks_accumulated)
        log_archive_path = self.create_logs_archive()

        try:
            send_status_ok = self.sender.send_document(chat_id=BotChat.LOGS_CHAT_ID.value,
                                                       caption=BotResponseMessage.PLANNED_LOG_UPLOAD.value,
                                                       document_path=log_archive_path).ok
        except FileNotFoundError as e:
            exception = str(e)

        if not send_status_ok:
            self.sender.send_message(chat_id=BotChat.LOGS_CHAT_ID.value,
                                     message=f"{BotResponseMessage.DAILY_LOG_SEND_FAIL.value}\n{exception}",
                                     disable_notification=True)
            return

        try:
            self.remove_archive(log_archive_path)
            self.clear_logs()
        except FileNotFoundError:
            pass
        self.scanner.drop_accumulated_networks()
        sleep(SleepDuration.INIT_REFRESH_FREQUENCY.value)
        self.scanner.refresh_networks()
        self.scanner.logger_working = False

    @retry()
    def schedule_routine(self):
        schedule.every().hour.do(self.hourly_log)
        (schedule.every().day.
         at(time_str=Option.DAILY_LOG_SCHEDULE_TIME.value, tz=Option.ALMATY_TIMEZONE.value).
         do(self.daily_log))

        while True:
            schedule.run_pending()
            sleep(SleepDuration.SCHEDULE_PENDING_FREQUENCY.value)
