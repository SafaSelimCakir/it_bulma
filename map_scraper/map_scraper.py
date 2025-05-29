import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from threading import Thread
from scraper.scraper import run_scraper_gui_input

class ScraperApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Google Maps Scraper")
        self.setGeometry(300, 300, 400, 200)

        layout = QVBoxLayout()

        self.city_label = QLabel("Şehir(ler) (virgülle ayırın):")
        layout.addWidget(self.city_label)

        self.city_input = QLineEdit()
        layout.addWidget(self.city_input)

        self.district_label = QLabel("İlçe(ler) (virgülle ayırın):")
        layout.addWidget(self.district_label)

        self.district_input = QLineEdit()
        layout.addWidget(self.district_input)

        self.start_button = QPushButton("Başlat")
        self.start_button.clicked.connect(self.start_scraping)
        layout.addWidget(self.start_button)

        self.setLayout(layout)

    def start_scraping(self):
        cities = self.city_input.text().strip()
        districts = self.district_input.text().strip()
        if not cities:
            QMessageBox.warning(self, "Uyarı", "Lütfen en az bir şehir girin.")
            return

        thread = Thread(target=self.run_scraper_thread, args=(cities, districts))
        thread.start()

    def run_scraper_thread(self, cities, districts):
        try:
            run_scraper_gui_input(cities, districts)
        except Exception as e:
            QMessageBox.critical(self, "Hata", str(e))

if __name__ == "__main__":
    app = QApplication(sys.argv)
    scraper_app = ScraperApp()
    scraper_app.show()
    sys.exit(app.exec_())
