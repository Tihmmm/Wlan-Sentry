from time import sleep, strftime

from gpiozero import CPUTemperature
from pandas import DataFrame
from retry import retry
from scapy.layers.dot11 import Dot11, Dot11Beacon, Dot11Elt


from pyric.pyw import Card, chset

from Constants import BotChat, SleepDuration, BotResponseMessage, Option, BotAllowedUser
from telegram_api_wrapper.Sender import Sender
from utils import format_dataframe


class Scanner:

    def __init__(self, sender: Sender, card: Card):
        networks_accumulated = (DataFrame(columns=["BSSID", "SSID", "dbm_signal", "Channel", "Encryption"]).
                                set_index("BSSID"))
        networks_current = (DataFrame(columns=["BSSID", "SSID", "dbm_signal", "Channel", "Encryption"]).
                            set_index("BSSID"))
        self.sender = sender
        self.networks_accumulated = networks_accumulated
        self.networks_current = networks_current
        self.card = card
        self.networks_being_refreshed = False
        self.logger_working = False
        self.cpu_temperature = 0

    @property
    def networks_accumulated(self) -> DataFrame:
        return self._networks_accumulated

    @networks_accumulated.setter
    def networks_accumulated(self, value: DataFrame):
        self._networks_accumulated = value

    @property
    def networks_current(self) -> DataFrame:
        return self._networks_current

    @networks_current.setter
    def networks_current(self, value: DataFrame):
        self._networks_current = value

    @property
    def card(self) -> Card:
        return self._card

    @card.setter
    def card(self, value: Card):
        self._card = value

    @property
    def networks_being_refreshed(self) -> bool:
        return self._networks_being_refreshed

    @networks_being_refreshed.setter
    def networks_being_refreshed(self, value: bool):
        self._networks_being_refreshed = value

    @property
    def logger_working(self) -> bool:
        return self._logger_working

    @logger_working.setter
    def logger_working(self, value: bool):
        self._logger_working = value

    def drop_accumulated_networks(self):
        self.networks_accumulated.drop(self.networks_accumulated.index, inplace=True)

    @property
    def cpu_temperature(self) -> float:
        return self._cpu_temperature

    @cpu_temperature.setter
    def cpu_temperature(self, value: float):
        self._cpu_temperature = value

    @staticmethod
    def is_it_eepy_time():
        return not Option.EEPY_TIME.value > strftime('%H:%M') > Option.WAKEY_WAKEY_TIME.value

    @retry()
    def callback(self, packet):
        if packet.haslayer(Dot11Beacon):
            bssid = packet[Dot11].addr2
            ssid = packet[Dot11Elt].info.decode()
            try:
                dbm_signal = packet.dBm_AntSignal
            except:
                dbm_signal = "N/A"
            stats = packet[Dot11Beacon].network_stats()
            channel = stats.get("channel")
            encryption = stats.get("crypto")
            self.networks_current.loc[bssid] = (ssid, dbm_signal, channel, encryption)

    def change_channel(self):
        ch = 1
        while True:
            chset(card=self.card, ch=ch)
            ch = ch % 13 + 1
            sleep(SleepDuration.CHANNEL_CHANGE_FREQUENCY.value)

    def accumulate(self):
        networks_accumulated_copy = self.networks_accumulated.copy()
        self.networks_accumulated = (self.networks_accumulated.
                                     merge(self.networks_current, on="BSSID", how="outer", suffixes=("_x", None)).
                                     drop(["SSID_x", "dbm_signal_x", "Channel_x", "Encryption_x"], axis=1))
        self.networks_accumulated.update(networks_accumulated_copy)
        del networks_accumulated_copy

    def refresh_networks(self):
        if self.networks_being_refreshed:
            sleep(SleepDuration.DELAYED_REFRESH_FREQUENCY.value)
        else:
            self.networks_being_refreshed = True
            self.accumulate()
            self.networks_current.drop(self.networks_current.index, inplace=True)
            sleep(SleepDuration.REFRESH_FREQUENCY.value)
            self.networks_being_refreshed = False

    @retry()
    def compare(self):
        while True:
            if not self.logger_working:
                joined_df = (self.networks_accumulated.
                             merge(self.networks_current, on="BSSID", how="right", indicator=True, suffixes=("_x", None)).
                             loc[lambda x: x["_merge"] == "right_only"].
                             drop(["SSID_x", "dbm_signal_x", "Channel_x", "Encryption_x", "_merge"], axis=1))
                if not joined_df.empty:
                    output = f"""
                    {BotResponseMessage.JOINED.value} ({len(joined_df)}):\n\n{format_dataframe(joined_df, 'BSSID')}
                    """
                    self.sender.send_message(chat_id=BotChat.ALERTS_CHAT_ID.value,
                                             message=output,
                                             disable_notification=self.is_it_eepy_time())
                del joined_df
                self.refresh_networks()

    @retry()
    def monitor_cpu_temperature(self):
        while True:
            self.cpu_temperature = CPUTemperature().temperature
            if self.cpu_temperature >= float(Option.CPU_TEMPERATURE_THRESHOLD.value):
                self.sender.send_message(chat_id=BotAllowedUser.ALLOWED_USER_1.value, message=f"{BotResponseMessage.TEMPERATURE_TOO_HIGH.value}\n{self.cpu_temperature}")
            sleep(SleepDuration.TEMPERATURE_MONITOR_FREQUENCY.value)
