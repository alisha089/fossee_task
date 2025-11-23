import sys
import requests
import webbrowser
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QPushButton, QFileDialog, QLabel, QTableWidget, QTableWidgetItem, 
                             QHBoxLayout, QLineEdit, QDialog, QFormLayout, QMessageBox, 
                             QHeaderView, QListWidget, QListWidgetItem, QFrame)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import matplotlib.pyplot as plt

API_URL = "http://127.0.0.1:8000"

STYLESHEET = """
    QMainWindow, QDialog { background-color: #f4f6f9; }
    QLabel { color: #2d3748; }
    QLineEdit { background-color: white; color: #2d3748; border: 1px solid #cbd5e0; padding: 5px; border-radius: 4px; }
    QPushButton { background-color: #667eea; color: white; padding: 10px 15px; border-radius: 6px; font-weight: bold; border: none; font-size: 13px; }
    QPushButton:hover { background-color: #5a67d8; }
    QPushButton#Secondary { background-color: #cbd5e0; color: #2d3748; }
    QPushButton#Secondary:hover { background-color: #a0aec0; }
    QPushButton#Logout { background-color: transparent; color: #e53e3e; border: 1px solid #e53e3e; }
    QPushButton#Logout:hover { background-color: #fff5f5; }
    QListWidget { background-color: white; border: 1px solid #e2e8f0; border-radius: 8px; color: #2d3748; }
    QListWidget::item { padding: 10px; border-bottom: 1px solid #edf2f7; }
    QListWidget::item:selected { background-color: #ebf4ff; color: #2d3748; }
    QTableWidget { border: 1px solid #e2e8f0; background-color: white; color: #2d3748; gridline-color: #e2e8f0; selection-background-color: #ebf4ff; selection-color: #2d3748; }
    QHeaderView::section { background-color: #edf2f7; padding: 5px; border: 1px solid #e2e8f0; font-weight: bold; color: #4a5568; }
    QFrame#StatCard { background-color: white; border: 1px solid #e2e8f0; border-radius: 8px; }
    QLabel#StatValue { font-size: 18px; font-weight: bold; color: #667eea; }
    QLabel#StatLabel { font-size: 12px; color: #718096; font-weight: bold; text-transform: uppercase; }
"""

class HistoryDialog(QDialog):
    def __init__(self, history_data, auth, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Recent Uploads")
        self.resize(500, 400)
        self.auth = auth
        self.setStyleSheet(STYLESHEET)
        
        layout = QVBoxLayout(self)
        
        title = QLabel("Your Upload History")
        title.setStyleSheet("font-size: 16px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title)

        self.list_widget = QListWidget()
        layout.addWidget(self.list_widget)
        
        for idx, h in enumerate(history_data, 1):
            item = QListWidgetItem()
            widget = QWidget()
            h_layout = QHBoxLayout(widget)
            
            info_layout = QVBoxLayout()
            lbl_name = QLabel(f"{idx}. {h.get('filename', 'File')}")
            lbl_name.setStyleSheet("font-weight: bold;")
            lbl_date = QLabel(f"Date: {h.get('date', '-')}")
            lbl_date.setStyleSheet("font-size: 11px; color: #718096;")
            info_layout.addWidget(lbl_name)
            info_layout.addWidget(lbl_date)
            h_layout.addLayout(info_layout)
            
            h_layout.addStretch()
            
            btn_pdf = QPushButton("Download PDF")
            btn_pdf.setFixedSize(100, 30)
            btn_pdf.setStyleSheet("font-size: 11px; padding: 5px;")
            btn_pdf.clicked.connect(lambda checked, uid=h['id']: self.download_pdf(uid))
            h_layout.addWidget(btn_pdf)
            
            item.setSizeHint(widget.sizeHint())
            self.list_widget.addItem(item)
            self.list_widget.setItemWidget(item, widget)
            
        btn_close = QPushButton("Close")
        btn_close.setObjectName("Secondary")
        btn_close.clicked.connect(self.accept)
        layout.addWidget(btn_close)

    def download_pdf(self, upload_id):
        path, _ = QFileDialog.getSaveFileName(self, "Save PDF", f"report_{upload_id}.pdf", "PDF Files (*.pdf)")
        if path:
            try:
                res = requests.get(f"{API_URL}/api/pdf/{upload_id}/", auth=self.auth)
                if res.status_code == 200:
                    with open(path, 'wb') as f:
                        f.write(res.content)
                    QMessageBox.information(self, "Success", "PDF Saved Successfully")
                else:
                    QMessageBox.warning(self, "Error", "Failed to download PDF")
            except Exception as e:
                QMessageBox.critical(self, "Error", str(e))

class SignupDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Create Account")
        self.resize(350, 180)
        self.setStyleSheet(STYLESHEET) 
        
        layout = QFormLayout()
        self.user_in = QLineEdit()
        self.pass_in = QLineEdit()
        self.pass_in.setEchoMode(QLineEdit.Password)
        
        layout.addRow("New Username:", self.user_in)
        layout.addRow("New Password:", self.pass_in)
        
        self.btn_create = QPushButton("Create Account")
        self.btn_create.clicked.connect(self.register)
        layout.addRow(self.btn_create)
        self.setLayout(layout)
        
    def register(self):
        username = self.user_in.text()
        password = self.pass_in.text()
        if not username or not password: return
        try:
            response = requests.post(f"{API_URL}/api/register/", 
                                   data={"username": username, "password": password})
            if response.status_code == 201:
                QMessageBox.information(self, "Success", "Account Created")
                self.accept()
            else:
                QMessageBox.critical(self, "Error", "Username exists.")
        except: pass

class LoginDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Login")
        self.setGeometry(100, 100, 350, 200)
        self.setStyleSheet(STYLESHEET)
        
        layout = QFormLayout()
        self.username_input = QLineEdit()
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        
        layout.addRow("Username:", self.username_input)
        layout.addRow("Password:", self.password_input)
        
        self.login_btn = QPushButton("Login")
        self.login_btn.clicked.connect(self.accept)
        
        self.signup_btn = QPushButton("Create New Account")
        self.signup_btn.setObjectName("Secondary")
        self.signup_btn.clicked.connect(self.open_signup)
        
        layout.addRow(self.login_btn)
        layout.addRow(self.signup_btn)
        self.setLayout(layout)
    
    def open_signup(self):
        SignupDialog().exec_()
    
    def get_credentials(self):
        return self.username_input.text(), self.password_input.text()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Chemical Equipment Visualizer")
        self.resize(1200, 850)
        self.auth = None
        self.setStyleSheet(STYLESHEET)
        self.login()
        
    def login(self):
        dialog = LoginDialog()
        if dialog.exec_() == QDialog.Accepted:
            username, password = dialog.get_credentials()
            if not username or not password: sys.exit()
            try:
                self.auth = (username, password)
                requests.get(f"{API_URL}/api/history/", auth=self.auth)
                self.setup_ui()
            except: sys.exit()
        else: sys.exit()
    
    def setup_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        header = QHBoxLayout()
        title = QLabel("Chemical Equipment Visualizer")
        title.setStyleSheet("font-size: 20px; font-weight: bold;")
        self.lbl_status = QLabel("System Ready")
        header.addWidget(title)
        header.addStretch()
        header.addWidget(self.lbl_status)
        layout.addLayout(header)
        
        btns = QHBoxLayout()
        self.btn_upload = QPushButton("Upload CSV")
        self.btn_upload.clicked.connect(self.upload_file)
        
        self.btn_history = QPushButton("View History")
        self.btn_history.clicked.connect(self.show_history)
        self.btn_history.setObjectName("Secondary")
        
        self.btn_logout = QPushButton("Log Out")
        self.btn_logout.setObjectName("Logout")
        self.btn_logout.clicked.connect(self.close)
        
        btns.addWidget(self.btn_upload)
        btns.addWidget(self.btn_history)
        btns.addStretch()
        btns.addWidget(self.btn_logout)
        layout.addLayout(btns)

        self.stats_layout = QHBoxLayout()
        self.stats_labels = {}
        for key in ["Total Count", "Avg Flowrate", "Avg Pressure", "Avg Temperature"]:
            card = QFrame()
            card.setObjectName("StatCard")
            card_layout = QVBoxLayout(card)
            
            val_label = QLabel("-")
            val_label.setObjectName("StatValue")
            val_label.setAlignment(Qt.AlignCenter)
            
            title_label = QLabel(key)
            title_label.setObjectName("StatLabel")
            title_label.setAlignment(Qt.AlignCenter)
            
            card_layout.addWidget(title_label)
            card_layout.addWidget(val_label)
            
            self.stats_layout.addWidget(card)
            self.stats_labels[key] = val_label
            
        layout.addLayout(self.stats_layout)

        self.figure = plt.figure(figsize=(6, 3))
        self.figure.patch.set_facecolor('#f4f6f9')
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        self.table = QTableWidget()
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        layout.addWidget(self.table)

    def upload_file(self):
        fname, _ = QFileDialog.getOpenFileName(self, 'Open CSV', '', 'CSV Files (*.csv)')
        if fname:
            self.lbl_status.setText("Uploading...")
            try:
                with open(fname, 'rb') as f:
                    res = requests.post(f'{API_URL}/api/upload/', files={'file': f}, auth=self.auth)
                    if res.status_code == 200:
                        self.update_ui(res.json())
                        self.lbl_status.setText("Upload Complete")
                    else: self.lbl_status.setText("Failed")
            except: self.lbl_status.setText("Error")

    def update_ui(self, data):
        stats = data['stats']
        self.stats_labels["Total Count"].setText(str(stats['total_count']))
        self.stats_labels["Avg Flowrate"].setText(f"{stats['avg_flowrate']:.2f}")
        self.stats_labels["Avg Pressure"].setText(f"{stats['avg_pressure']:.2f}")
        self.stats_labels["Avg Temperature"].setText(f"{stats['avg_temperature']:.2f}")

        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.set_facecolor('#f8fafc')
        dist = data['distribution']
        bars = ax.bar(dist.keys(), dist.values(), color='#667eea', width=0.6)
        for bar in bars:
            ax.text(bar.get_x() + bar.get_width()/2., bar.get_height(),
                    f'{int(bar.get_height())}', ha='center', va='bottom', color='#2d3748')
        self.figure.tight_layout()
        self.canvas.draw()
        
        rows = data['data']
        if not rows: return
        self.table.setColumnCount(len(rows[0]))
        self.table.setRowCount(len(rows))
        self.table.setHorizontalHeaderLabels(rows[0].keys())
        for i, row in enumerate(rows):
            for j, val in enumerate(row.values()):
                self.table.setItem(i, j, QTableWidgetItem(str(val)))

    def show_history(self):
        try:
            res = requests.get(f'{API_URL}/api/history/', auth=self.auth)
            history = res.json()
            if not history:
                QMessageBox.information(self, "History", "No uploads found.")
                return
            
            dlg = HistoryDialog(history, self.auth, self)
            dlg.exec_()
            
        except:
            QMessageBox.critical(self, "Error", "Failed to fetch history")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setFont(QFont("Segoe UI", 10))
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
