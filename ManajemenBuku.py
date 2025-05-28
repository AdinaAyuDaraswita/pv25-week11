from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QAction,
    QMainWindow, QFileDialog, QMessageBox, QInputDialog,
    QDockWidget, QTextEdit, QStatusBar
)
from PyQt5.QtGui import QIcon, QClipboard
from PyQt5.QtWidgets import QToolButton
from PyQt5.QtWidgets import QScrollArea 
from PyQt5.QtCore import Qt, QTimer, QDateTime
import sqlite3
import csv
import sys

class BookManager(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Manajemen Buku")
        self.setGeometry(100, 100, 800, 500)

        self.setStyleSheet("""
            QWidget {
                background-color: #f0f4f8;
                font-family: Segoe UI, sans-serif;
                font-size: 13px;
            }
            QPushButton {
                background-color: #4a90e2;
                color: white;
                padding: 6px 12px;
                border: none;
                border-radius: 6px;
            }
            QPushButton:hover {
                background-color: #357ABD;
            }
            QLineEdit {
                background-color: #ffffff;
                padding: 4px;
                border: 1px solid #ccc;
                border-radius: 4px;
            }
            QTableWidget {
                background-color: #ffffff;
                alternate-background-color: #f9f9f9;
            }
            QHeaderView::section {
                background-color: #dce3ed;
                padding: 6px;
                font-weight: bold;
                border: none;
            }
            QMenuBar {
                background-color: #f0f4f8;
            }
            QMenuBar::item {
                background-color: transparent;
                color: #333333;
                padding: 5px 20px;
                margin: 0 2px;
            }
            QMenuBar::item:selected {
                background-color: #4a90e2;
                color: white;
            }
            QMenu {
                background-color: #f0f4f8;
                color: #333333;
                border: 1px solid #ccc;
            }
            QMenu::item {
                background-color: transparent;
                color: #333333;
                padding: 4px 20px;
            }
            QMenu::item:selected {
                background-color: #4a90e2;
                color: white;
            }
        """)

        self.conn = sqlite3.connect("books.db")
        self.init_db()

        self.create_menu()
        self.init_ui()
        self.init_dock_widget()
        self.init_status_bar()

        self.btn_data.setStyleSheet("background-color: #357ABD; color: white;")
        self.btn_export.setStyleSheet("")


        self.load_data()

    def init_db(self):
        cursor = self.conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS books (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT,
                author TEXT,
                year INTEGER
            )
        """)
        self.conn.commit()

    def create_menu(self):
        menubar = self.menuBar()

        file_menu = menubar.addMenu("File")
        simpan_action = QAction(QIcon("D:\SEMESTER 6\Pemrograman Visual\Tugas\AssigmentWeek10\save.png"), "Simpan", self)
        simpan_action.triggered.connect(self.save_data)
        ekspor_action = QAction(QIcon("D:\SEMESTER 6\Pemrograman Visual\Tugas\AssigmentWeek10\export.png"), "Ekspor ke CSV", self)
        ekspor_action.triggered.connect(self.export_to_csv)
        keluar_action = QAction(QIcon("D:\SEMESTER 6\Pemrograman Visual\Tugas\AssigmentWeek10\exit.png"), "Keluar", self)
        keluar_action.triggered.connect(self.close)
        file_menu.addAction(simpan_action)
        file_menu.addAction(ekspor_action)
        file_menu.addAction(keluar_action)

        edit_menu = menubar.addMenu("Edit")
        cari_action = QAction("Cari Judul", self)
        cari_action.triggered.connect(lambda: self.search_bar.setFocus())
        hapus_action = QAction("Hapus Data", self)
        hapus_action.triggered.connect(self.delete_data)
        autofill_action = QAction("AutoFill", self)
        start_dict_action = QAction("Start Dictation...", self)
        emoji_action = QAction("Emoji & Symbols", self)
        edit_menu.addAction(cari_action)
        edit_menu.addAction(hapus_action)
        edit_menu.addAction(autofill_action)
        edit_menu.addAction(start_dict_action)
        edit_menu.addAction(emoji_action)

    def init_ui(self):
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout()

        tab_layout = QHBoxLayout()
        tab_layout.addStretch()
        self.btn_data = QPushButton("Data Buku")
        self.btn_export = QPushButton("Ekspor")
        self.btn_data.setCheckable(True)
        self.btn_export.setCheckable(True)
        self.btn_data.setChecked(True)
        self.btn_data.setFixedWidth(100)
        self.btn_export.setFixedWidth(100)
        self.btn_data.clicked.connect(lambda: self.switch_tab("data"))
        self.btn_export.clicked.connect(lambda: self.switch_tab("export"))
        tab_layout.addWidget(self.btn_data)
        tab_layout.addWidget(self.btn_export)
        tab_layout.addStretch()
        layout.addLayout(tab_layout)

        self.halaman_data = self.buatTabData()
        self.halaman_export = self.buatTabExport()

        layout.addWidget(self.halaman_data)
        layout.addWidget(self.halaman_export)

        self.halaman_data.show()
        self.halaman_export.hide()

        central_widget.setLayout(layout)

    def init_dock_widget(self):
        self.log_dock = QDockWidget("Riwayat Aksi", self)
        self.log_dock.setAllowedAreas(Qt.LeftDockWidgetArea | Qt.RightDockWidgetArea)

        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #ffffff;
                border: 1px solid #ccc;
                padding: 8px;
                font-family: Consolas, monospace;
                font-size: 12px;
                border-radius: 6px;
            }
        """)

        self.log_dock.setWidget(self.log_text)
        self.addDockWidget(Qt.RightDockWidgetArea, self.log_dock)

    def init_status_bar(self):
        self.status = QStatusBar()
        self.setStatusBar(self.status)

        self.label_nama_nim = QLabel("Nama: Adina Ayu Daraswita | NIM: F1D022030")
        self.status.addPermanentWidget(self.label_nama_nim)


        self.update_time()
        timer = QTimer(self)
        timer.timeout.connect(self.update_time)
        timer.start(1000)

    def update_time(self):
        now = QDateTime.currentDateTime()
        time_str = now.toString("dddd, dd MMMM yyyy hh:mm:ss")
        self.status.showMessage(f"Tanggal & Waktu Saat Ini: {time_str}")

    def log_action(self, message):
        self.log_text.append(message)

    

    def buatTabData(self):
        widget = QWidget()
        layout = QVBoxLayout()

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)

        form_container = QWidget()
        form_inner_layout = QVBoxLayout()

        row_title = QHBoxLayout()
        row_title.addWidget(QLabel("Judul:"))

        judul_container = QWidget()
        judul_layout = QHBoxLayout()
        judul_layout.setContentsMargins(0, 0, 0, 0)

        self.judulBuku = QLineEdit()
        self.btn_clipboard_icon = QToolButton()
        self.btn_clipboard_icon.setIcon(QIcon("D:/SEMESTER 6/Pemrograman Visual/Tugas/AssigmentWeek10/paste.png"))  
        
        self.btn_clipboard_icon.setToolTip("Tempel dari Clipboard")
        self.btn_clipboard_icon.setCursor(Qt.PointingHandCursor)
        self.btn_clipboard_icon.setStyleSheet("border: none; padding: 0px;")

        self.btn_clipboard_icon.clicked.connect(self.paste_title_from_clipboard)

        judul_layout.addWidget(self.judulBuku)
        judul_layout.addWidget(self.btn_clipboard_icon)
        judul_container.setLayout(judul_layout)

        row_title.addWidget(judul_container)
        form_inner_layout.addLayout(row_title)

        row_author = QHBoxLayout()
        row_author.addWidget(QLabel("Pengarang:"))
        self.input_author = QLineEdit()
        row_author.addWidget(self.input_author)
        form_inner_layout.addLayout(row_author)

        row_year = QHBoxLayout()
        row_year.addWidget(QLabel("Tahun:"))
        self.input_year = QLineEdit()
        row_year.addWidget(self.input_year)
        form_inner_layout.addLayout(row_year)

        self.btn_save = QPushButton("Simpan")
        self.btn_save.clicked.connect(self.save_data)
        form_inner_layout.addWidget(self.btn_save)

        form_layout = QHBoxLayout()
        form_layout.addStretch()
        form_layout.addLayout(form_inner_layout)
        form_layout.addStretch()

        form_container.setLayout(form_layout)
        scroll_area.setWidget(form_container)
        layout.addWidget(scroll_area)

        self.search_bar = QLineEdit()
        self.search_bar.setPlaceholderText("Cari judul...")
        self.search_bar.textChanged.connect(self.search_data)

        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["ID", "Judul", "Pengarang", "Tahun"])
        self.table.cellDoubleClicked.connect(self.edit_data)


        self.table.setHorizontalScrollMode(QTableWidget.ScrollPerPixel)
        self.table.setVerticalScrollMode(QTableWidget.ScrollPerPixel)
        self.table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)

        self.btn_delete = QPushButton("Hapus Data")
        self.btn_delete.setStyleSheet("background-color: orange;")
        self.btn_delete.clicked.connect(self.delete_data)

        layout.addWidget(self.search_bar)
        layout.addWidget(self.table)
        layout.addWidget(self.btn_delete)

        widget.setLayout(layout)

        return widget

    


    def paste_title_from_clipboard(self):
        clipboard = QApplication.clipboard()
        text = clipboard.text()
        if text:
            self.judulBuku.setText(text)
            self.log_action(f"Tempel judul dari clipboard: {text}")
        else:
            QMessageBox.information(self, "Info", "Clipboard kosong atau tidak berisi teks.")

    def buatTabExport(self):
        widget = QWidget()
        layout = QVBoxLayout()
        self.btn_export = QPushButton("Ekspor ke CSV")
        self.btn_export.clicked.connect(self.export_to_csv)
        layout.addWidget(self.btn_export)
        widget.setLayout(layout)
        return widget

    def switch_tab(self, name):
        if name == "data":
            self.btn_data.setChecked(True)
            self.btn_export.setChecked(False)
            self.halaman_data.show()
            self.halaman_export.hide()
            self.btn_data.setStyleSheet("background-color: #357ABD; color: white;")
            self.btn_export.setStyleSheet("")
        else:
            self.btn_data.setChecked(False)
            self.btn_export.setChecked(True)
            self.halaman_data.hide()
            self.halaman_export.show()
            self.btn_export.setStyleSheet("background-color: #357ABD; color: white;")
            self.btn_data.setStyleSheet("")

    def save_data(self):
        title = self.judulBuku.text()
        author = self.input_author.text()
        year = self.input_year.text()
        if not title or not author or not year:
            QMessageBox.warning(self, "Peringatan", "Harap isi semua field sebelum menyimpan!")
            return
        cursor = self.conn.cursor()
        cursor.execute("INSERT INTO books (title, author, year) VALUES (?, ?, ?)", (title, author, year))
        self.conn.commit()
        self.log_action(f"Simpan buku: {title} oleh {author} ({year})")
        self.clear_form()
        self.load_data()

    def load_data(self):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM books")
        records = cursor.fetchall()
        self.table.setRowCount(0)
        for row_num, row_data in enumerate(records):
            self.table.insertRow(row_num)
            for col_num, data in enumerate(row_data):
                self.table.setItem(row_num, col_num, QTableWidgetItem(str(data)))

    def search_data(self, text):
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM books WHERE title LIKE ?", ('%' + text + '%',))
        records = cursor.fetchall()
        self.table.setRowCount(0)
        for row_num, row_data in enumerate(records):
            self.table.insertRow(row_num)
            for col_num, data in enumerate(row_data):
                self.table.setItem(row_num, col_num, QTableWidgetItem(str(data)))

    def edit_data(self, row, column):
        if column not in (1, 2, 3):
            return

        id_buku = int(self.table.item(row, 0).text())
        current_value = self.table.item(row, column).text()

        if column == 1:
            field = "title" ; label = "Ubah Judul"
        elif column == 2:
            field = "author" ; label = "Ubah Pengarang"
        else:
            field = "year" ; label = "Ubah Tahun"

        new_value, ok = QInputDialog.getText(self, label, f"Edit {label}:", text=current_value)
        if ok and new_value:
            cursor = self.conn.cursor()
            cursor.execute(f"UPDATE books SET {field} = ? WHERE id = ?", (new_value, id_buku))
            self.conn.commit()
            self.log_action(f"Edit {field} id {id_buku}: {new_value}")
            self.load_data()

    def delete_data(self):
        selected_rows = self.table.selectionModel().selectedRows()
        if not selected_rows:
            QMessageBox.warning(self, "Peringatan", "Pilih data yang akan dihapus!")
            return

        reply = QMessageBox.question(self, 'Konfirmasi', 'Yakin ingin menghapus data yang dipilih?', QMessageBox.Yes | QMessageBox.No, QMessageBox.No)
        if reply == QMessageBox.Yes:
            cursor = self.conn.cursor()
            for index in selected_rows:
                id_buku = int(self.table.item(index.row(), 0).text())
                cursor.execute("DELETE FROM books WHERE id = ?", (id_buku,))
                self.log_action(f"Hapus data buku id {id_buku}")
            self.conn.commit()
            self.load_data()

    def clear_form(self):
        self.judulBuku.clear()
        self.input_author.clear()
        self.input_year.clear()

    def export_to_csv(self):
        path, _ = QFileDialog.getSaveFileName(self, "Simpan File CSV", "", "CSV Files (*.csv)")
        if path:
            cursor = self.conn.cursor()
            cursor.execute("SELECT * FROM books")
            records = cursor.fetchall()
            try:
                with open(path, mode='w', newline='', encoding='utf-8') as file:
                    writer = csv.writer(file)
                    writer.writerow(["ID", "Judul", "Pengarang", "Tahun"])
                    writer.writerows(records)
                self.log_action(f"Ekspor data berhasil: {path}")
                QMessageBox.information(self, "Sukses", "Data berhasil diekspor ke CSV.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Gagal ekspor data: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = BookManager()
    window.show()
    sys.exit(app.exec())
