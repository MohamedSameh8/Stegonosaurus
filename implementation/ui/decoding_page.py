from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QGraphicsView, QGraphicsScene, QHBoxLayout, QFileDialog, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QWheelEvent, QPalette, QColor
from steganography import Steganography
import pyperclip

class DecodingPage(QWidget):
    def __init__(self):
        super().__init__()
        self.steganography = None
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self) # create vertical layout
        
        self.image_label = QLabel("Select image to decode data:") # img selection label
        layout.addWidget(self.image_label) # add label to layout
        
        self.image_path = QLineEdit()
        layout.addWidget(self.image_path) # add input field to layout
        
        self.browse_button = QPushButton("Browse") # browse button
        self.browse_button.clicked.connect(self._browse_image) # connect browse button to browse_image method
        layout.addWidget(self.browse_button)
        
        self.preview_label = QLabel("Preview:")
        layout.addWidget(self.preview_label)
        
        self.image_view = ZoomableGraphicsView() # view for image
        self.image_scene = QGraphicsScene()
        self.image_view.setScene(self.image_scene) # set scene for view
        layout.addWidget(self.image_view)
        
        self.status_label = QLabel("Config Status:")
        layout.addWidget(self.status_label)
        
        self.status_bar = QWidget()
        self.status_bar.setFixedHeight(20) # set fixed height
        self._set_status_bar_color("red") # default color for json status
        layout.addWidget(self.status_bar)
        
        self._init_buttons(layout)
        self._init_decoded_text_output(layout)

    def _init_buttons(self, layout):
        config_button_layout = QHBoxLayout() # horizontal layout for config buttons
        
        self.load_config_button = QPushButton("Load Config")
        self.load_config_button.setToolTip("Load a configuration.") # tooltip for load button
        self.load_config_button.clicked.connect(self._load_config) # connect load button to load_config method
        config_button_layout.addWidget(self.load_config_button)
        
        self.unload_config_button = QPushButton("Unload Config")
        self.unload_config_button.setToolTip("Unload the current configuration.")
        self.unload_config_button.clicked.connect(self._unload_config)
        config_button_layout.addWidget(self.unload_config_button)
        
        layout.addLayout(config_button_layout)
        
        self.decode_button = QPushButton("Decode")
        self.decode_button.setToolTip("Start the decoding process.")
        self.decode_button.clicked.connect(self._decode_data)
        layout.addWidget(self.decode_button)

    def _init_decoded_text_output(self, layout):
        self.decoded_text_label = QLabel("Decoded Text:")
        layout.addWidget(self.decoded_text_label)
        
        self.decoded_text_output = QLineEdit() # text field for decoded text
        self.decoded_text_output.setReadOnly(True) # read-only text field
        decoded_text_layout = QHBoxLayout()
        decoded_text_layout.addWidget(self.decoded_text_output)

        self.copy_button = QPushButton("Copy")
        self.copy_button.clicked.connect(self._copy_text)        
        decoded_text_layout.addWidget(self.copy_button)

        layout.addLayout(decoded_text_layout)

    def _browse_image(self):
        try:
            file_path, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Images (*.png *.jpg *.bmp)") # get image file path
            if file_path:
                self.image_path.setText(file_path) # set image path in input field
                pixmap = QPixmap(file_path) # create pixmap from image
                self.image_scene.addPixmap(pixmap) # add pixmap to scene
        except Exception as e:
            self._show_error_message(f"Error browsing image: {e}.\nMake sure the file is an image.")

    def _load_config(self):
        try:
            file_path, _ = QFileDialog.getOpenFileName(self, "Select Config File", "", "JSON Files (*.json);;All Files (*)")
            if file_path:
                config = Steganography.load_config(file_path) # load config from file
                if self._validate_config(config): # validate config using _validate_config method
                    self.steganography = Steganography(config)
                    self._set_status_bar_color("green") # set status bar color to green
                    self.status_label.setText("Config Status: Loaded")
                else: # if config is invalid
                    self._set_status_bar_color("orange")
                    self.status_label.setText("Config Status: Invalid")
                    self._show_error_message("Invalid configuration file.") # show error message popup
            else:
                self.status_label.setText("Failed to load config.") # set status label to failed if no file is selected
        except Exception as e:
            self._show_error_message(f"Error loading config: {e}.\nMake sure the file is a valid JSON file.")

    def _validate_config(self, config):
        # config requirements
        required_keys = ["algorithm", "encryption", "noise_level"]
        valid_algorithms = ["X Significant Bit", "Pixel Value Differencing"]
        valid_encryptions = ["None", "Base64", "AES"]
        
        for key in required_keys:
            if key not in config:
                return False
        if config["algorithm"] not in valid_algorithms:
            return False
        if config["encryption"] not in valid_encryptions:
            return False
        if config["encryption"] == "AES" and ("key" not in config or "iv" not in config):
            return False
        if config["algorithm"] == "X Significant Bit" and "bit_position" not in config:
            return False
        return True # all config checks passed

    def _unload_config(self):
        self.steganography = None # set steganography object to None
        self._set_status_bar_color("red") # set status bar color to red
        self.status_label.setText("Config Status: Unloaded")

    def _set_status_bar_color(self, color):
        palette = self.status_bar.palette() # get palette
        palette.setColor(QPalette.ColorRole.Window, QColor(color)) # set color
        self.status_bar.setAutoFillBackground(True) # fill background
        self.status_bar.setPalette(palette)

    def _decode_data(self):
        try:
            if self.steganography:
                image_path = self.image_path.text()
                decoded_text = self.steganography.decode_text(image_path) # attempt to decode text
                self.decoded_text_output.setText(decoded_text) # set decoded text in output field
        except Exception as e:
            self._show_error_message(f"Error decoding data: {e}.\nMake sure your config file is correct.")

    def _copy_text(self):
        decoded_text = self.decoded_text_output.text() # get decoded text
        pyperclip.copy(decoded_text) # copy text to clipboard

    def _show_error_message(self, message):
        error_dialog = QMessageBox()
        error_dialog.setIcon(QMessageBox.Icon.Critical) # set error icon
        error_dialog.setText(message)
        error_dialog.setWindowTitle("Error")
        copy_button = error_dialog.addButton("Copy", QMessageBox.ButtonRole.ActionRole) # add copy button
        copy_button.clicked.connect(lambda: pyperclip.copy(message)) # copy error message to clipboard
        error_dialog.exec()

    def _show_info_message(self, message):
        info_dialog = QMessageBox()
        info_dialog.setIcon(QMessageBox.Icon.Information) # set info icon
        info_dialog.setText(message)
        info_dialog.setWindowTitle("Info") # set window title
        info_dialog.exec()

class ZoomableGraphicsView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag) # set drag mode to scroll hand drag
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse) # set transformation anchor to under mouse

    def wheelEvent(self, event: QWheelEvent): # method to handle wheel events
        zoom_in_factor = 1.25
        zoom_out_factor = 1 / zoom_in_factor
        zoom_factor = zoom_in_factor if event.angleDelta().y() > 0 else zoom_out_factor # set zoom factor based on wheel direction
        self.scale(zoom_factor, zoom_factor)