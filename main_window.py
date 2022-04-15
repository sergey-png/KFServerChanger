from PyQt5 import QtWidgets, QtCore, QtGui
import requests
import sys
import time
from bs4 import BeautifulSoup
from threading import Thread

from base import Ui_MainWindow
import auth_token


class MyApp(QtWidgets.QMainWindow):
    def __init__(self):
        super(MyApp, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.urls = {
            "server_admin": "http://212.22.93.74:20570/ServerAdmin",
            "server_info": "http://212.22.93.74:20570/ServerAdmin/current/info",
            "server_change_map": "http://212.22.93.74:20570/ServerAdmin/current/change"
        }
        self.__auth_tokens = auth_token.auth_token
        self.game_types = {
            "Survival": "KFGameContent.KFGameInfo_Survival",
            "Versus Survival": "KFGameContent.KFGameInfo_VersusSurvival",
            "Endless": "KFGameContent.KFGameInfo_Endless",
            "Weekly": "KFGameContent.KFGameInfo_Weekly"
        }
        self.game_maps = ['KF-Airship',
                          'KF-AshwoodAsylum',
                          'KF-Biolapse',
                          'KF-BioticsLab',
                          'KF-BlackForest',
                          'KF-BurningParis',
                          'KF-Bus_Depot',
                          'KF-CarillonHamlet',
                          'KF-Catacombs',
                          'KF-ContainmentStation',
                          'KF-De_Dust2',
                          'KF-DeepingWall',
                          'KF-Default',
                          'KF-Desolation',
                          'KF-DieSector',
                          'KF-Dystopia2029',
                          'KF-Elysium',
                          'KF-EvacuationPoint',
                          'KF-Farm_Remastered',
                          'KF-Farmhouse',
                          'KF-Farmhouse2',
                          'KF-HellmarkStation',
                          'KF-HostileGrounds',
                          'KF-InfernalRealm',
                          'KF-KF1_Manor',
                          'KF-KF1_West_London',
                          'KF-Kino_Der_Toten',
                          'KF-KrampusLair',
                          'KF-Lockdown',
                          'KF-MonsterBall',
                          'KF-Moonbase',
                          'KF-Netherhold',
                          'KF-Nightmare',
                          'KF-Nuked',
                          'KF-Offices',
                          'KF-Outpost',
                          'KF-PowerCore_Holdout',
                          'KF-Prison',
                          'KF-Sanitarium',
                          'KF-SantasWorkshop',
                          'KF-ShoppingSpree',
                          'KF-Spillway',
                          'KF-SteamFortress',
                          'KF-TheDescent',
                          'KF-TragicKingdom',
                          'KF-VolterManor',
                          'KF-ZedLanding']

        self.game_type = ""  # current game type
        self.game_map = ""  # current game map
        self.game_length = ""  # current game length
        self.difficulty = ""  # current game difficulty
        self.mutator = False  # current game mutator

        self.init_ui()

        self.ui.pushButton.clicked.connect(self.connect_to_server)
        self.ui.pushButton_2.clicked.connect(self.change_map)
        self.ui.pushButton_3.clicked.connect(self.get_info)
        # При нажатии на виджеты с игровыми параметрами происходит изменение параметров игры
        self.ui.listWidget.itemClicked.connect(self.change_game_map)
        self.ui.listWidget_2.itemClicked.connect(self.change_game_type)
        self.ui.listWidget_3.itemClicked.connect(self.change_game_length)
        self.ui.listWidget_4.itemClicked.connect(self.change_difficulty)
        self.ui.listWidget_5.itemClicked.connect(self.change_mutator)

    def init_ui(self):
        self.ui.pushButton.setEnabled(True)
        self.ui.pushButton.setText("Connect to server")
        self.ui.pushButton.setStyleSheet("")  # default style
        self.ui.tabWidget.setCurrentIndex(0)
        self.ui.listWidget.clear()
        self.ui.pushButton_3.setEnabled(True)
        for element in self.game_maps:
            self.ui.listWidget.addItem(element[3:])

    def connect_to_server(self):
        self.ui.pushButton.setEnabled(False)
        self.ui.pushButton.setText("Connecting...")
        check_connection = self.check_connection()
        if check_connection is True:
            self.ui.pushButton.setText("Connected")
            self.ui.pushButton.setStyleSheet("background-color: rgb(0, 170, 0);color: rgb(255, 255, 255);")  # green
            self.ui.tabWidget.setCurrentIndex(1)
            self.ui.pushButton_3.setEnabled(True)
        else:
            self.ui.pushButton.setText("Connection failed")
            self.ui.pushButton.setStyleSheet("background-color: rgb(170, 0, 0);color: rgb(255, 255, 255);")  # red
            self.ui.pushButton.setEnabled(True)

    def check_connection(self):
        url = self.urls["server_admin"]
        try:
            requests.request("GET", url)
            return True
        except Exception as error_msg:
            print(error_msg)
            return False

    def get_info(self):
        self.ui.pushButton_3.setEnabled(False)
        if self.check_connection() is False:
            self.ui.pushButton_3.setEnabled(True)
            self.ui.tabWidget.setCurrentIndex(0)
            self.ui.pushButton.setEnabled(True)
            self.ui.pushButton.setText("Connect to server")
            self.ui.pushButton.setStyleSheet("")  # default style
            return

        url = self.urls["server_info"]
        payload = {}
        headers = {
            "Authorization": self.__auth_tokens["server_admin_main"]
        }
        response = requests.request("GET", url, headers=headers, data=payload)
        soup = BeautifulSoup(response.text, "lxml")
        # find all dt and dd elements
        dt_elements = soup.find_all("dt")
        dd_elements = soup.find_all("dd")
        dt_elements_text = [dt_element.text for dt_element in dt_elements]
        dd_elements_text = [dd_element.text for dd_element in dd_elements]
        # make dict with key:value pairs from dt and dd elements
        info_dict = dict(zip(dt_elements_text, dd_elements_text))
        # set values to rows of tableWidget
        set_list = ["Map", "Players", "Wave", "Game type", "Difficulty", "Spectators", "Mutators"]
        values = []
        for set_list_element in set_list:
            if info_dict.get(set_list_element) is None:
                values.append("")
            else:
                values.append(info_dict[set_list_element])
        for i, val in enumerate(values):
            if i == 6 and val == "":
                self.ui.tableWidget.setItem(i, 0, QtWidgets.QTableWidgetItem("No mutators"))
            else:
                self.ui.tableWidget.setItem(i, 0, QtWidgets.QTableWidgetItem(val))
        thread = Thread(target=waiting_for_server, daemon=True)
        thread.start()
        return

    def change_map(self):
        self.ui.pushButton_2.setEnabled(False)
        self.ui.pushButton_3.setEnabled(False)
        if self.check_connection() is False:
            self.ui.pushButton_2.setEnabled(True)
            self.ui.tabWidget.setCurrentIndex(0)
            self.ui.pushButton.setEnabled(True)
            self.ui.pushButton.setText("Connect to server")
            self.ui.pushButton.setStyleSheet("")  # default style
            return
        if self.game_map == "" or self.game_length == "" or self.difficulty == "" or self.game_type == "":
            self.ui.pushButton_2.setEnabled(True)
            # show error message box
            msg = QtWidgets.QMessageBox()
            msg.setIcon(QtWidgets.QMessageBox.Critical)
            msg.setText("Заполните все поля")
            msg.setWindowTitle("Error")
            msg.exec_()
            return

        url = self.urls["server_change_map"]
        if self.mutator:
            mutator = '?mutator=FriendlyHUD.FriendlyHUDMutator'
        else:
            mutator = ''
        urlextra = f'?GameLength={self.game_length}?MaxPlayers=6?Difficulty={self.difficulty}' + mutator
        payload = {'gametype': self.game_type,
                   'map': self.game_map,
                   'mutatorGroupCount': '0',
                   'urlextra': urlextra,
                   'action': 'change'
                   }
        headers = {
            "Authorization": self.__auth_tokens["server_admin_main"]
        }
        requests.request("POST", url, headers=headers, data=payload)
        thread = Thread(target=waiting_for_server, daemon=True)
        thread.start()
        return

    def change_game_length(self, item: QtWidgets.QTableWidgetItem):
        self.game_length = item.text()
        self.ui.tableWidget_2.setItem(1, 0, QtWidgets.QTableWidgetItem(self.game_length))
        game_length_dict = {
            "4": "0",
            "7": "1",
            "10": "2"
        }
        self.game_length = game_length_dict[self.game_length]
        print(f"Game length changed to {self.game_length}")
        return

    def change_difficulty(self, item: QtWidgets.QTableWidgetItem):
        self.difficulty = item.text()
        self.ui.tableWidget_2.setItem(3, 0, QtWidgets.QTableWidgetItem(self.difficulty))
        difficulty_dict = {
            "Easy": "0",
            "Hard": "1",
            "Suicidal": "2",
            "Hell on Earth": "3"
        }
        self.difficulty = difficulty_dict[self.difficulty]
        print(f"Difficulty changed to {self.difficulty}")
        return

    def change_game_type(self, item: QtWidgets.QTableWidgetItem):
        self.game_type = item.text()
        self.ui.tableWidget_2.setItem(2, 0, QtWidgets.QTableWidgetItem(self.game_type))
        self.game_type = self.game_types[self.game_type]
        print(f"Game type changed to {self.game_type}")
        return

    def change_game_map(self, item: QtWidgets.QTableWidgetItem):
        self.game_map = item.text()
        self.ui.tableWidget_2.setItem(0, 0, QtWidgets.QTableWidgetItem(self.game_map))
        self.game_map = f"KF-{item.text()}"
        print(f"Game map changed to {self.game_map}")
        return

    def change_mutator(self, item):
        if item.text() == "None":
            self.mutator = False
        else:
            self.mutator = True
        print(f"Mutator changed to {self.mutator}")
        self.ui.tableWidget_2.setItem(4, 0, QtWidgets.QTableWidgetItem(item.text()))
        return


def waiting_for_server():
    global window
    # wait for server to change map
    time.sleep(10)
    window.ui.pushButton_3.setEnabled(True)
    window.ui.pushButton_2.setEnabled(True)
    return


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = MyApp()
    window.show()
    sys.exit(app.exec_())
