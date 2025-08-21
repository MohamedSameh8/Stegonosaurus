from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QTabWidget
from .encoding_page import EmbeddingPage
from .conversion_page import ConversionPage
from .config_page import ConfigPage
from .decoding_page import DecodingPage

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Image Steganography")
        self.setGeometry(100, 100, 800, 600) # default size, extendable
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget) # main window central widget
        self.layout = QVBoxLayout(self.central_widget) # central widget layout
        self.tabs = QTabWidget()
        self.layout.addWidget(self.tabs) # tab widget for different pages
        
        # create pages with linked python files
        self.embedding_page = EmbeddingPage()
        self.conversion_page = ConversionPage()
        self.config_page = ConfigPage()
        self.decoding_page = DecodingPage()
        
        # add pages to tab widget
        self.tabs.addTab(self.embedding_page, "Embed Data")
        self.tabs.addTab(self.decoding_page, "Decode Data")
        self.tabs.addTab(self.config_page, "Config Generator")
        self.tabs.addTab(self.conversion_page, "Image Conversion")