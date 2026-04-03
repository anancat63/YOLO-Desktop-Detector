from __future__ import annotations

import sys
import warnings

import cv2
from PySide6.QtCore import QTimer, Qt
from PySide6.QtGui import QFont, QGuiApplication, QIcon, QPixmap
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QTableWidgetItem,
    QWidget,
)

from ui.UiMain import Ui_MainWindow

from . import config as Config
from . import detect_tools as tools
from .database import authenticate_user, create_user, get_user_by_username
from .framework import DetectorFramework
from .manage import UserManagement

warnings.filterwarnings("ignore")


class MainWindow(QMainWindow):
    def __init__(self, username: str, parent=None):
        super().__init__(parent)
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.username = username
        self.detector = DetectorFramework()
        self.conf = self.detector.default_conf
        self.iou = self.detector.default_iou

        self.cap = None
        self.is_camera_open = False
        self.org_path: str | None = None

        self.timer_camera = QTimer(self)
        self.timer_camera.timeout.connect(self.open_frame)

        self.init_main()
        self.bind_events()

    def init_main(self):
        app_cfg = Config.get_project_config()
        window_cfg = Config.get_window_config()

        self.setWindowTitle(str(app_cfg.get("app_name", "Object Detection System")))
        self.setFixedSize(window_cfg["width"], window_cfg["height"])
        self.show_width = window_cfg["show_width"]
        self.show_height = window_cfg["show_height"]

        self.ui.tableWidget.verticalHeader().setSectionResizeMode(QHeaderView.Fixed)
        self.ui.tableWidget.verticalHeader().setDefaultSectionSize(40)
        self.ui.tableWidget.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.ui.tableWidget.verticalHeader().setVisible(False)
        self.ui.tableWidget.setAlternatingRowColors(True)

        self.ui.label_welcome.setText(f"Welcome, {self.username}!")
        if self.username != "admin":
            self.ui.UserBtn.setVisible(False)

    def bind_events(self):
        self.ui.PicBtn.clicked.connect(self.open_img)
        self.ui.VideoBtn.clicked.connect(self.video_show)
        self.ui.CapBtn.clicked.connect(self.camera_show)
        self.ui.UserBtn.clicked.connect(self.user_manage)
        self.ui.ExitBtn.clicked.connect(self.exit_login)
        self.ui.tableWidget.cellClicked.connect(self.on_cell_clicked)

    def clear_table(self):
        self.ui.tableWidget.setRowCount(0)
        self.ui.tableWidget.clearContents()

    def stop_stream(self):
        if self.cap and self.cap.isOpened():
            self.cap.release()
        self.cap = None
        self.timer_camera.stop()

    def get_resize_size(self, img):
        img_h, img_w = img.shape[:2]
        ratio = img_w / img_h
        if ratio >= self.show_width / self.show_height:
            width = self.show_width
            height = int(width / ratio)
        else:
            height = self.show_height
            width = int(height * ratio)
        return width, height

    def render_image(self, img):
        if img is None:
            return
        width, height = self.get_resize_size(img)
        resized = cv2.resize(img, (width, height))
        pix = tools.cvimg_to_qpiximg(resized)
        self.ui.label_show.setPixmap(pix)
        self.ui.label_show.setAlignment(Qt.AlignCenter)

    def show_table_result(self, pred, path=""):
        for loc, cls_id, conf, target_id in zip(
            pred["locations"], pred["classes"], pred["confidences"], pred["ids"]
        ):
            row = self.ui.tableWidget.rowCount()
            self.ui.tableWidget.insertRow(row)
            values = [
                str(row + 1),
                "" if self.is_camera_open else path,
                str(target_id),
                Config.get_class_name(int(cls_id), "zh"),
                str(conf),
                str(loc),
            ]
            for col, value in enumerate(values):
                item = QTableWidgetItem(value)
                item.setTextAlignment(Qt.AlignHCenter | Qt.AlignVCenter)
                self.ui.tableWidget.setItem(row, col, item)
        self.ui.tableWidget.scrollToBottom()

    def open_img(self):
        self.stop_stream()
        self.is_camera_open = False
        self.ui.VideolineEdit.setText("请选择视频文件")
        self.ui.CaplineEdit.setText("摄像头未开启")

        path, _ = QFileDialog.getOpenFileName(self, "打开图片", "./", "Image files (*.jpg *.jpeg *.png *.bmp)")
        if not path:
            return

        self.org_path = path
        self.ui.PiclineEdit.setText(path)

        pred = self.detector.predict(path, conf=self.conf, iou=self.iou)
        self.render_image(pred["plot"])
        self.clear_table()
        self.show_table_result(pred, path=path)

    def get_video_path(self):
        path, _ = QFileDialog.getOpenFileName(self, "打开视频", "./", "Video files (*.avi *.mp4 *.wmv *.mkv)")
        return path or None

    def start_video_loop(self):
        self.clear_table()
        self.timer_camera.start(1)

    def open_frame(self):
        if not self.cap:
            return
        ok, frame = self.cap.read()
        if not ok:
            self.stop_stream()
            self.ui.VideolineEdit.setText("请选择视频文件")
            return

        pred = self.detector.predict(frame, conf=self.conf, iou=self.iou)
        self.render_image(pred["plot"])
        self.show_table_result(pred, path=self.org_path or "")

    def video_show(self):
        self.ui.PiclineEdit.setText("请选择图片文件")

        if self.is_camera_open:
            self.is_camera_open = False
            self.ui.CaplineEdit.setText("摄像头未开启")
            self.stop_stream()

        if self.cap and self.cap.isOpened():
            self.ui.VideolineEdit.setText("请选择视频文件")
            self.ui.label_show.clear()
            self.stop_stream()
            return

        path = self.get_video_path()
        if not path:
            return

        self.org_path = path
        self.ui.VideolineEdit.setText(path)
        self.cap = cv2.VideoCapture(path)
        self.start_video_loop()

    def camera_show(self):
        self.ui.PiclineEdit.setText("请选择图片文件")
        self.is_camera_open = not self.is_camera_open

        if self.is_camera_open:
            self.ui.VideolineEdit.setText("请选择视频文件")
            self.ui.CaplineEdit.setText("摄像头已开启")
            self.cap = cv2.VideoCapture(0)
            self.start_video_loop()
        else:
            self.ui.CaplineEdit.setText("摄像头未开启")
            self.ui.label_show.clear()
            self.stop_stream()

    def on_cell_clicked(self, row, _column):
        if self.cap or self.is_camera_open:
            return
        path_item = self.ui.tableWidget.item(row, 1)
        if not path_item:
            return
        path = path_item.text().strip()
        if not path:
            return
        pred = self.detector.predict(path, conf=self.conf, iou=self.iou)
        self.render_image(pred["plot"])

    def user_manage(self):
        self.win = UserManagement()
        self.win.show()

    def exit_login(self):
        self.stop_stream()
        self.win = LoginForm()
        self.win.show()
        self.close()


class LoginForm(QWidget):
    def __init__(self):
        super().__init__()
        self.led_workerid = QLineEdit()
        self.led_pwd = QLineEdit()
        self.btn_login = QPushButton("Login")
        self.btn_reg = QPushButton("Register")

        self.init_ui()
        self.btn_login.clicked.connect(self.do_login)
        self.btn_reg.clicked.connect(self.do_reg)

    def init_ui(self):
        self.setObjectName("loginWindow")
        self.setStyleSheet("#loginWindow{background:transparent;}")
        self.setFixedSize(650, 400)
        self.setWindowTitle("Login")
        self.setWindowIcon(QIcon(Config.resolve_path("ui/icon/fruit.png")))

        self.cover_pixmap = QPixmap(Config.resolve_path("ui/img/img.png"))
        self.cover_label = QLabel(self)
        self.cover_label.setGeometry(0, 0, self.width(), self.height())
        self.cover_label.setAlignment(Qt.AlignCenter)
        self.cover_label.setStyleSheet("background-color:#1f1f1f;")
        self.update_cover()

        title = QLabel("Object Detection System Login", self)
        title.setStyleSheet("QWidget{color:white;font-weight:600;background: transparent;font-size:30px;}")
        title.setFont(QFont("Microsoft YaHei"))
        title.move(140, 70)
        title.setAlignment(Qt.AlignCenter)
        title.raise_()

        box = QWidget(self)
        box.setGeometry(0, 120, 650, 250)

        hbox = QHBoxLayout()
        logo_label = QLabel(self)
        logo = QPixmap(Config.resolve_path("ui/img/水果.png")).scaled(150, 150)
        logo_label.setPixmap(logo)
        logo_label.setAlignment(Qt.AlignCenter)
        hbox.addWidget(logo_label, 1)

        form = QFormLayout()
        for label, widget, is_pwd in (("Username", self.led_workerid, False), ("Password", self.led_pwd, True)):
            lbl = QLabel(label)
            lbl.setFont(QFont("Microsoft YaHei"))
            widget.setFixedWidth(270)
            widget.setFixedHeight(38)
            widget.setFont(QFont("Microsoft YaHei"))
            widget.setPlaceholderText(label)
            if is_pwd:
                widget.setEchoMode(QLineEdit.Password)
            form.addRow(lbl, widget)

        self.btn_reg.setFixedSize(130, 40)
        self.btn_login.setFixedSize(130, 40)
        row = QHBoxLayout()
        row.addWidget(self.btn_reg)
        row.addWidget(self.btn_login)
        form.addRow(row)

        hbox.addLayout(form, 2)
        box.setLayout(hbox)
        box.setStyleSheet(
            "QWidget{background:transparent;} QLabel{color:white;} QLineEdit{background:rgba(255,255,255,0.92);border-radius:4px;padding:4px 8px;} QPushButton{background-color:#2c7adf;color:#fff;border-radius:4px;}"
        )

        self.center()

    def update_cover(self):
        if self.cover_pixmap.isNull():
            return
        scaled = self.cover_pixmap.scaled(self.cover_label.size(), Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)
        self.cover_label.setPixmap(scaled)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if hasattr(self, "cover_label"):
            self.cover_label.setGeometry(0, 0, self.width(), self.height())
            self.update_cover()

    def center(self):
        geo = self.frameGeometry()
        center = QGuiApplication.primaryScreen().availableGeometry().center()
        geo.moveCenter(center)
        self.move(geo.topLeft())

    def do_reg(self):
        username = self.led_workerid.text().strip()
        password = self.led_pwd.text().strip()
        if not username or not password:
            QMessageBox.about(self, "Registration", "Information is incomplete!\nPlease re-enter username and password.")
            return
        try:
            if not create_user(username, password):
                QMessageBox.about(self, "Registration", f"User {username} is already registered!")
                return
            QMessageBox.about(self, "Registration", f"User {username} registered successfully!")
        except Exception as err:
            QMessageBox.critical(self, "Database Error", f"Registration failed: {err}")

    def do_login(self):
        username = self.led_workerid.text().strip()
        password = self.led_pwd.text().strip()
        if not username or not password:
            QMessageBox.about(self, "Login", "Information is incomplete!\nPlease re-enter username and password.")
            return
        try:
            user = get_user_by_username(username)
            if not user:
                QMessageBox.about(self, "Login", f"User {username} is not registered!")
                return
            if authenticate_user(username, password):
                self.win = MainWindow(username)
                self.win.show()
                self.close()
            else:
                QMessageBox.about(self, "Login", f"Incorrect password for user {username}!")
        except Exception as err:
            QMessageBox.critical(self, "Database Error", f"Login failed: {err}")


def run() -> int:
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)

    db_notice = Config.init_database()

    app = QApplication(sys.argv)
    if db_notice:
        QMessageBox.information(None, "Database Notice", db_notice)

    win = LoginForm()
    win.show()
    return app.exec()


if __name__ == "__main__":
    sys.exit(run())
