import os
from enum import Enum

import utils


class ExtendedEnum(Enum):

    @classmethod
    def list(cls):
        return list(map(lambda c: c.value, cls))


class Option(str, ExtendedEnum):
    INTERFACE = "wlan0mon"
    PHINDEX = "0"
    IFINDEX = "4"
    MONITOR_MODE = "monitor"
    DAILY_LOG_SCHEDULE_TIME = "17:00"
    WAKEY_WAKEY_TIME = "09:00"
    EEPY_TIME = "22:00"
    ALMATY_TIMEZONE = ""
    ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
    LOGS_DIR_NAME = "daily_logs"
    LOGS_DIR_PATH = f"{ROOT_DIR}/{LOGS_DIR_NAME}"
    GENERIC_SUCCESS = "success"
    GENERIC_FAIL = "fail"
    MESSAGE_LENGTH_LIMIT = "4096"
    MARKDOWN_PARSE_MODE = "MarkdownV2"
    NETWORKS_ACCUMULATED_FILE_NAME = "networks_accumulated"
    CPU_TEMPERATURE_THRESHOLD = "80"


class SleepDuration(float, ExtendedEnum):
    CHANNEL_CHANGE_FREQUENCY = 0.3
    CHANNEL_COUNT = 14
    CHANNEL_WALKS = 4
    REFRESH_FREQUENCY = CHANNEL_CHANGE_FREQUENCY * CHANNEL_COUNT * CHANNEL_WALKS
    INIT_REFRESH_FREQUENCY = REFRESH_FREQUENCY * 12
    DELAYED_REFRESH_FREQUENCY = REFRESH_FREQUENCY + 0.3
    SCHEDULE_PENDING_FREQUENCY = 20
    BOT_POLL_TIMEOUT = 60
    TEMPERATURE_MONITOR_FREQUENCY = 3


class BotAllowedUser(str, ExtendedEnum):
    ALLOWED_USER_1 = ""
    ALLOWED_USER_2 = ""


class BotCommand(str, ExtendedEnum):
    NETWORKS_CURRENT = "/networks_current"
    NETWORKS_ACCUMULATED = "/networks_accumulated"
    GET_LOGS_DIRECTORY = "/logs_dir"
    GET_LOGS_ARCHIVE = "/logs_archive"
    CLEAR_LOGS = "/clear_logs"
    GET_CPU_TEMPERATURE = "/cpu"
    GET_CONTROLLER_COMMAND = "/controller"


class BotControllerOption(str, ExtendedEnum):
    RESTART_SNIFFER = "/sniffer"
    RESTART_CHANNEL_CHANGER = "/channels"
    RESTART_SCHEDULER = "/scheduler"
    RESTART_CPU_MONITOR = "/monitor"
    RESTART_ALL_CORE_THREADS = "/all_core"


class BotChat(str, Enum):
    TOKEN = ""
    BASE_URL = f"https://api.telegram.org/bot{TOKEN}"
    ALERTS_CHAT_ID = ""
    LOGS_CHAT_ID = ""
    COMMANDS_DEFINED = utils.format_list(BotCommand.list())
    CONTROLLER_COMMANDS = utils.format_list(BotControllerOption.list())


class BotResponseMessage(str, Enum):
    INITIALIZED = "Network monitoring initialized"
    GENERIC_FAIL = "Error"
    NETWORK_DOWN = f"Interface {Option.INTERFACE.value} is not available!"
    JOINED = "Joined"
    CURRENT = "Current networks"
    ACCUMULATED = "Accumulated networks"
    DAILY_LOG_SEND_FAIL = "LOG UPLOAD FAILURE!"
    LOGS_REMOVE_SUCCESS = "Logs directory is successfully cleared"
    PLANNED_LOG_UPLOAD = "Daily log upload"
    UNPLANNED_LOG_UPLOAD = "Unplanned log upload"
    UNPLANNED_LOG_REMOVE = "Unplanned log removal"
    REQUEST_ACCEPTED = "Request accepted"
    COMMAND_NOT_DEFINED = f"This command is undefined.\nAvailable commands:\n\n{BotChat.COMMANDS_DEFINED.value}"
    TEMPERATURE_TOO_HIGH = "High CPU temperature!"
