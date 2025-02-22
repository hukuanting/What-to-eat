from PyQt5 import QtCore, QtWidgets
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtWidgets import QInputDialog, QGraphicsPixmapItem, QGraphicsView, QGraphicsScene
import cv2
import random
from ui import Ui_MainWindow
import googlemaps
import math
from PyQt5.QtCore import QStringListModel

gmaps = googlemaps.Client(key='AIzaSyCiI_vKg-YEu3P7yQTDqPg9AdIBmLZJmPk')

def calculate_bearing(lat1, lon1, lat2, lon2):
    """
    Calculate the bearing (direction) from point A to point B.
    Inputs are the latitude and longitude of both points in decimal degrees.
    Returns the bearing in degrees (clockwise from north).
    """
    # Convert decimal degrees to radians
    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    # Calculate differences in longitudes and latitudes
    delta_lon = lon2 - lon1

    # Calculate bearing
    y = math.sin(delta_lon) * math.cos(lat2)
    x = math.cos(lat1) * math.sin(lat2) - math.sin(lat1) * math.cos(lat2) * math.cos(delta_lon)
    bearing_rad = math.atan2(y, x)

    # Convert bearing from radians to degrees
    bearing_deg = math.degrees(bearing_rad)

    # Normalize to a compass bearing (0 to 360 degrees)
    bearing_deg = (bearing_deg + 360) % 360

    return bearing_deg


def get_direction(bearing):
    directions = ["北", "東北", "東", "東南", "南", "西南", "西", "西北"]
    index = round(bearing / 45) % 8
    return directions[index]


def calculate_distance(lat1, lon1, lat2, lon2, unit='km'):
    # approximate radius of earth in km
    R = 6371.0 if unit == 'km' else 3956.0

    # convert degrees to radians
    lat1 = math.radians(lat1)
    lon1 = math.radians(lon1)
    lat2 = math.radians(lat2)
    lon2 = math.radians(lon2)

    # calculate change in coordinates
    dlon = lon2 - lon1
    dlat = lat2 - lat1

    # apply Haversine formula
    a = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

    # calculate distance
    distance = R * c

    return distance


class MainWindow_controller(QtWidgets.QMainWindow):

    def __init__(self):
        super().__init__()  # in python3, super(Class, self).xxx = super().xxx

        self.i = 20
        self.model = None
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.ui.pushButton.clicked.connect(self.finding)
        self.ui.pushButton_2.clicked.connect(self.ran)
        self.ui.addloc.clicked.connect(self.addloc)
        self.ui.addtype.clicked.connect(self.addtype)

        loc_icon = cv2.resize(cv2.imread('Google_Maps_icon.png'), (49, 49))
        scene = QGraphicsScene()
        scene.addItem(QGraphicsPixmapItem(QPixmap.fromImage(QImage(loc_icon, 49, 49, 3 * 49, QImage.Format_BGR888))))
        self.ui.loc_icon.setScene(scene)

        type_icon = cv2.resize(cv2.imread('food.png'), (49, 49))
        scene = QGraphicsScene()
        scene.addItem(QGraphicsPixmapItem(QPixmap.fromImage(QImage(type_icon, 49, 49, 3 * 49, QImage.Format_BGR888))))
        self.ui.type_icon.setScene(scene)

        self.ui.location.addItem("國立成功大學生物醫學工程學系")
        self.ui.location.addItem("701台南市東區東寧路120巷20號")
        self.ui.location.addItem("403台中市西區巷上路一段29巷52號")

        self.ui.location_2.addItem("餐廳")
        self.ui.location_2.addItem("飯")
        self.ui.location_2.addItem("麵")
        self.ui.location_2.addItem("水餃")
        self.ui.location_2.addItem("滷味")
        self.ui.location_2.addItem("牛肉湯")
        self.ui.location_2.addItem("泰式料理")
        self.ui.location_2.addItem("日式料理")
        self.ui.location_2.addItem("韓式料理")
        self.ui.location_2.addItem("美式料理")
        self.ui.location_2.addItem("義式料理")
        self.ui.location_2.addItem("甜點")

        self.ui.direction.setMinimum(0)
        self.ui.direction.setMaximum(360)
        self.direction = ''
        self.ui.direction.valueChanged.connect(self.on_dial_changed)

        self.uber = False
        self.ui.uber.stateChanged.connect(self.on_checkbox_changed)

        self.distance = 0.0
        self.ui.horizontalSlider.setMinimum(0)  # 设置最小值
        self.ui.horizontalSlider.setMaximum(100)  # 设置最大值
        self.ui.horizontalSlider.valueChanged.connect(self.on_slider_changed)

        self.ui.horizontalSlider.valueChanged.connect(self.on_slider_changed)

        self.model = QStringListModel()
        self.ui.listView.setModel(self.model)

    def addloc(self):
        text, okPressed = QInputDialog.getText(self, "新增選項", "請輸入地點:")
        if okPressed and text != '':
            self.ui.location.addItem(text)

    def addtype(self):
        text, okPressed = QInputDialog.getText(self, "新增選項", "請輸入種類:")
        if okPressed and text != '':
            self.ui.location_2.addItem(text)
    def finding(self):
        def add_data(data):
            self.model.setStringList(data)
        try:
            geocode_result = gmaps.geocode(self.ui.location.currentText())[0]
            location = geocode_result['geometry']['location']
            lat1, lng1 = location['lat'], location['lng']

            if self.uber:
                self.distance = 10

            places_result = gmaps.places_nearby(location, keyword=self.ui.location_2.currentText(),
                                                radius=self.distance * 1000)

            target = []
            output = []
            direction, length = None, None
            for place in places_result['results']:

                lat2, lng2 = place['geometry']['location']['lat'], place['geometry']['location']['lng']
                direction = get_direction(calculate_bearing(lat1, lng1, lat2, lng2))

                if place['business_status'] == 'OPERATIONAL':
                    if self.direction == '北':
                        if direction == '東北' or '西北' or '北':
                            target.append(place)

                    elif self.direction == '西':
                        if direction == '西北' or '西南' or '西':
                            target.append(place)

                    elif self.direction == '南':
                        if direction == '西南' or '東南' or '南':
                            target.append(place)

                    else:
                        if direction == '東南' or '東北' or '東':
                            target.append(place)

            self.i = 0
            for place in target:
                try:
                    price = place['price_level']
                except:
                    price = None
                try:
                    open_or_not = place['opening_hours']['open_now']
                except:
                    open_or_not = None
                try:
                    length = calculate_distance(lat1, lng1, lat2, lng2)
                except:
                    length = None
                self.i += 1
                output.append('{}. 店名：{}\nGoogle評分：{} 有開嗎：{}  價格：{}\n方位：{}邊 {:.2f}km\n'
                              .format(self.i, place['name'], place['rating'], open_or_not, price, direction, length))

            if output:
                add_data(output)
            else:
                add_data(['查無選項'])
        except:
            add_data(['查無選項，嘗試輸入地址或更精的type'])

    def ran(self):
        num = random.randint(1, self.i)
        self.ui.pushButton_2.setText(str(num))
    def on_dial_changed(self, value):
        if value < 45 or value >= 315:
            self.direction = "南"
        elif 45 <= value < 135:
            self.direction = "西"
        elif 135 <= value < 225:
            self.direction = "北"
        else:
            self.direction = "東"

    def on_checkbox_changed(self):
        if self.uber:
            self.uber = False
        else:
            self.uber = True

    def on_slider_changed(self, value):
        self.distance = value / 10.0


if __name__ == '__main__':
    import sys

    app = QtWidgets.QApplication(sys.argv)
    mainWindow = MainWindow_controller()
    mainWindow.show()
    sys.exit(app.exec_())
