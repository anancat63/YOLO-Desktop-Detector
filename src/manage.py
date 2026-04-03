import sys
from PySide6 import QtWidgets, QtCore
from PySide6.QtWidgets import QWidget

from ui.Management import Ui_Form
from .database import fetch_users, delete_user, update_user


class UserManagement(QWidget, Ui_Form):
    def __init__(self, parent=None):
        super(UserManagement, self).__init__(parent)
        self.setupUi(self)
        self.table.setColumnCount(4)

        self.table.setHorizontalHeaderLabels(['ID', '用户名', '密码', '操作'])
        self.table.verticalHeader().setVisible(False)

        self.table.setFixedWidth(700)
        self.table.setColumnWidth(0, 60)
        self.table.setColumnWidth(1, 200)
        self.table.setColumnWidth(2, 200)
        self.table.setColumnWidth(3, 240)
        self.table.setVerticalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.table.setHorizontalScrollBarPolicy(QtCore.Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        self.load_table_data()

    def load_table_data(self):
        users = fetch_users()
        self.table.setRowCount(len(users))

        for row_idx, user in enumerate(users):
            user_id, username, password = user

            self.table.setItem(row_idx, 0, QtWidgets.QTableWidgetItem(str(user_id)))
            self.table.setItem(row_idx, 1, QtWidgets.QTableWidgetItem(username))
            self.table.setItem(row_idx, 2, QtWidgets.QTableWidgetItem(password))

            self.table.item(row_idx, 0).setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            self.table.item(row_idx, 1).setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            self.table.item(row_idx, 2).setTextAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            self.table.setRowHeight(row_idx, 50)

            edit_button = QtWidgets.QPushButton('编辑')
            delete_button = QtWidgets.QPushButton('删除')

            edit_button.setStyleSheet(
                """
                QPushButton {background-color: #4CAF50; color: white; border: none; padding: 5px 10px; font-size: 14px; border-radius: 8px;}
                QPushButton:hover {background-color: #45a049;}
                """
            )
            delete_button.setStyleSheet(
                """
                QPushButton {background-color: #f44336; color: white; border: none; padding: 5px 10px; font-size: 14px; border-radius: 8px;}
                QPushButton:hover {background-color: #e53935;}
                """
            )

            if username == "admin":
                delete_button.setDisabled(True)
                delete_button.setStyleSheet(
                    """
                    QPushButton {background-color: #cccccc; color: white; border: none; padding: 5px 10px; font-size: 14px; border-radius: 8px;}
                    """
                )

            edit_button.clicked.connect(lambda _, u_id=user_id: self.edit_user(u_id))
            delete_button.clicked.connect(lambda _, u_id=user_id: self.delete_user_confirm(u_id))

            button_widget = QtWidgets.QWidget()
            button_layout = QtWidgets.QHBoxLayout()
            button_layout.addWidget(edit_button)
            button_layout.addWidget(delete_button)
            button_layout.setContentsMargins(0, 0, 0, 0)
            button_widget.setLayout(button_layout)
            self.table.setCellWidget(row_idx, 3, button_widget)

    def find_row_by_id(self, user_id):
        for row in range(self.table.rowCount()):
            if self.table.item(row, 0).text() == str(user_id):
                return row
        return -1

    def edit_user(self, user_id):
        row = self.find_row_by_id(user_id)
        if row == -1:
            QtWidgets.QMessageBox.warning(self, "错误", "未找到用户")
            return

        current_username = self.table.item(row, 1).text()
        current_password = self.table.item(row, 2).text()

        dialog = EditUserDialog(user_id, current_username, current_password)
        dialog.exec()
        self.load_table_data()

    def delete_user_confirm(self, user_id):
        confirm = QtWidgets.QMessageBox.question(
            self,
            '确认删除',
            '您确定要删除此用户吗？',
            QtWidgets.QMessageBox.StandardButton.Yes | QtWidgets.QMessageBox.StandardButton.No,
        )
        if confirm == QtWidgets.QMessageBox.StandardButton.Yes:
            delete_user(user_id)
            self.load_table_data()


class EditUserDialog(QtWidgets.QDialog):
    def __init__(self, user_id, current_username, current_password):
        super().__init__()

        self.user_id = user_id
        self.setWindowTitle('编辑用户')
        self.setStyleSheet(
            """
            QDialog {background-color: #ffffff; border-radius: 10px;}
            QLabel {font-size: 16px; margin-bottom: 5px;}
            QLineEdit {padding: 10px; border: 1px solid #ccc; border-radius: 5px; font-size: 14px;}
            QPushButton {background-color: #0078d7; color: white; border: none; padding: 10px; font-size: 14px; border-radius: 5px;}
            QPushButton:hover {background-color: #005bb5;}
            """
        )

        self.layout = QtWidgets.QVBoxLayout()
        self.layout.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)

        self.username_input = QtWidgets.QLineEdit()
        self.username_input.setText(current_username)
        self.layout.addWidget(QtWidgets.QLabel('用户名:'))
        self.layout.addWidget(self.username_input)

        self.password_input = QtWidgets.QLineEdit()
        self.password_input.setText(current_password)
        self.layout.addWidget(QtWidgets.QLabel('密码:'))
        self.layout.addWidget(self.password_input)

        self.save_button = QtWidgets.QPushButton('保存')
        self.save_button.clicked.connect(self.save_user)
        self.layout.addWidget(self.save_button)

        self.setLayout(self.layout)

    def save_user(self):
        new_username = self.username_input.text().strip()
        new_password = self.password_input.text().strip()
        if not new_username or not new_password:
            QtWidgets.QMessageBox.warning(self, '提示', '用户名和密码不能为空')
            return

        update_user(self.user_id, new_username, new_password)
        self.accept()


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    window = UserManagement()
    window.show()
    sys.exit(app.exec())
