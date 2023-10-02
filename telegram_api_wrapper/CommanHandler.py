import os

from Constants import BotResponseMessage, BotCommand, Option, BotChat, BotAllowedUser, BotControllerOption
from Scanner import Scanner
from telegram_api_wrapper.Sender import Sender
from utils import format_dataframe, format_directory_tree, create_text_file
from thread_controller import start_sniffer, start_sec_thread, start_all_core_threads

import Logger


class CommandHandler:

    def __init__(self, sender: Sender, scanner: Scanner, logger: Logger):
        self.sender = sender
        self.scanner = scanner
        self.logger = logger

    def handle_networks_accumulated_command(self, user_id: str):
        networks_accumulated_df = self.scanner.networks_accumulated
        networks_accumulated = f"""
        {BotResponseMessage.ACCUMULATED.value} ({len(networks_accumulated_df)}):\n\n{format_dataframe(
            dataframe=networks_accumulated_df,
            header='BSSID')}
        """
        if len(networks_accumulated) > int(Option.MESSAGE_LENGTH_LIMIT.value):
            networks_accumulated_file_path = f"{Option.LOGS_DIR_PATH.value}/{Option.NETWORKS_ACCUMULATED_FILE_NAME.value}.txt"
            with (open(networks_accumulated_file_path, "w+")
                  as networks_accumulated_file):
                networks_accumulated_file.write(networks_accumulated)
            self.sender.send_document(chat_id=user_id, document_path=networks_accumulated_file.name,
                                      disable_notification=False)
            os.remove(networks_accumulated_file_path)
        else:
            self.sender.send_message(chat_id=user_id, message=networks_accumulated)

    def handle_networks_current_command(self, user_id: str):
        networks_current_df = self.scanner.networks_current
        networks_current = f"""
        {BotResponseMessage.CURRENT.value} ({len(networks_current_df)}):\n\n{format_dataframe(
            dataframe=networks_current_df,
            header='BSSID')}
        """
        if len(networks_current) > int(Option.MESSAGE_LENGTH_LIMIT.value):
            for x in range(0, len(networks_current), int(Option.MESSAGE_LENGTH_LIMIT.value)):
                self.sender.send_message(chat_id=user_id,
                                         message=networks_current[x: x + int(Option.MESSAGE_LENGTH_LIMIT.value)])
        else:
            self.sender.send_message(chat_id=user_id, message=networks_current)

    def handle_get_logs_dir_command(self, user_id: str):
        logs_directory_tree = str(format_directory_tree(directory_path=Option.LOGS_DIR_PATH.value))
        self.sender.send_message(chat_id=user_id, message=logs_directory_tree)

    def handle_get_logs_archive_command(self, user_id: str):
        networks_accumulated_file_path = f"{Option.LOGS_DIR_PATH.value}/{Option.NETWORKS_ACCUMULATED_FILE_NAME.value}.txt"
        networks_accumulated = format_dataframe(self.scanner.networks_accumulated, header="BSSID")
        create_text_file(path=networks_accumulated_file_path, content=networks_accumulated)
        log_archive_path = self.logger.create_logs_archive()
        self.sender.send_document(chat_id=BotChat.LOGS_CHAT_ID.value, document_path=log_archive_path, parse_mode=Option.MARKDOWN_PARSE_MODE.value,
                                  caption=f"{BotResponseMessage.UNPLANNED_LOG_UPLOAD.value}, запрошенная [этим](tg://user?id={user_id}) пользователем",
                                  disable_notification=True)
        self.logger.remove_archive(log_archive_path)

    def handle_clear_logs_command(self, user_id: str):
        status = self.logger.clear_logs()
        if status == Option.GENERIC_SUCCESS.value:
            self.sender.send_message(chat_id=BotChat.LOGS_CHAT_ID.value, parse_mode=Option.MARKDOWN_PARSE_MODE.value,
                                     message=f"{BotResponseMessage.UNPLANNED_LOG_REMOVE.value}, запрошенная [этим](tg://user?id={user_id}) пользователем",
                                     disable_notification=True)
            self.sender.send_message(chat_id=user_id, message=BotResponseMessage.LOGS_REMOVE_SUCCESS.value)
        else:
            self.sender.send_message(chat_id=user_id, message=f"{BotResponseMessage.GENERIC_FAIL.value}\n{status}")

    def handle_cpu_command(self):
        cpu_temperature = self.scanner.cpu_temperature
        self.sender.send_message(chat_id=BotAllowedUser.ALLOWED_USER_1.value, message=str(cpu_temperature))
    
    def handle_get_controller_command(self, user_id: str):
        self.sender.send_message(chat_id=user_id, message=BotChat.CONTROLLER_COMMANDS.value)
    
    def handle_restart_sniffer_command(self):
        start_sniffer(self.scanner)

    def handle_restart_channel_changer_command(self):
        start_sec_thread(target=self.scanner.change_channel)
        
    def handle_restart_scheduler_command(self):
        start_sec_thread(target=self.logger.schedule_routine)
        
    def handle_restart_cpu_monitor_command(self):
        start_sec_thread(target=self.scanner.monitor_cpu_temperature)
    
    def handle_restart_all_core_threads_command(self):
        start_all_core_threads(self.sender, self.scanner, self.logger)

    def handle_command_not_found(self, user_id: str):
        self.sender.send_message(chat_id=user_id, message=BotResponseMessage.COMMAND_NOT_DEFINED.value)

    def handle_command(self, command: str, user_id: str):
        
        match command:
        
            case BotCommand.NETWORKS_ACCUMULATED.value:
                self.handle_networks_accumulated_command(user_id=user_id)
            case BotCommand.NETWORKS_CURRENT.value:
                self.handle_networks_current_command(user_id=user_id)
            case BotCommand.GET_LOGS_DIRECTORY.value:
                self.handle_get_logs_dir_command(user_id=user_id)
            case BotCommand.GET_LOGS_ARCHIVE.value:
                self.handle_get_logs_archive_command(user_id=user_id)
            case BotCommand.CLEAR_LOGS.value:
                self.handle_clear_logs_command(user_id=user_id)
            case BotCommand.GET_CPU_TEMPERATURE.value:
                self.handle_cpu_command()
                
            case BotCommand.GET_CONTROLLER_COMMAND.value:
                self.handle_get_controller_command(user_id=user_id)
            case BotControllerOption.RESTART_SNIFFER.value:
                self.handle_restart_sniffer_command()
            case BotControllerOption.RESTART_CHANNEL_CHANGER.value:
                self.handle_restart_channel_changer_command()
            case BotControllerOption.RESTART_SCHEDULER.value:
                self.handle_restart_scheduler_command()
            case BotControllerOption.RESTART_CPU_MONITOR.value:
                self.handle_restart_cpu_monitor_command()
            case BotControllerOption.RESTART_ALL_CORE_THREADS.value:
                self.handle_restart_all_core_threads_command()
            case _:
                self.handle_command_not_found(user_id=user_id)
