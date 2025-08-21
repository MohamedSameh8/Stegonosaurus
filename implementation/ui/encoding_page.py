from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QGraphicsView, QGraphicsScene, QHBoxLayout, QFileDialog, QMessageBox
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap, QWheelEvent, QPalette, QColor
from steganography import Steganography
import pyperclip
from PIL.ImageQt import ImageQt

class EmbeddingPage(QWidget):
    def __init__(self):
        super().__init__()
        self.steganography = None
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self) # create vertical layout
        
        self.image_label = QLabel("Select image to embed data:") # image selection label
        layout.addWidget(self.image_label) # add label to layout
        
        self.image_path = QLineEdit() # image path input field
        layout.addWidget(self.image_path) # add input field to layout
        
        self.browse_button = QPushButton("Browse")
        self.browse_button.clicked.connect(self._browse_image) # connect browse button to browse_image method
        layout.addWidget(self.browse_button) # add browse button to layout
        
        self.preview_label = QLabel("Preview:")
        layout.addWidget(self.preview_label)
        
        self.original_image_view = ZoomableGraphicsView() # view for original image
        self.stego_image_view = ZoomableGraphicsView()
        self.original_scene = QGraphicsScene() # scene for original image
        self.stego_scene = QGraphicsScene()
        self.original_image_view.setScene(self.original_scene) # set scene for original image view
        self.stego_image_view.setScene(self.stego_scene)
        
        self.original_image_view.companion_view = self.stego_image_view # link the views for synchronized zooming and scrolling
        self.stego_image_view.companion_view = self.original_image_view
        
        preview_layout = QHBoxLayout()
        preview_layout.addWidget(self.original_image_view) # add original image view to layout
        preview_layout.addWidget(self.stego_image_view)
        layout.addLayout(preview_layout)
        
        self.embed_text_input = QLineEdit() # text input field for embedding
        self.embed_text_input.setPlaceholderText("Enter text to embed")
        embed_text_layout = QHBoxLayout() # horizontal layout for embedding text
        embed_text_layout.addWidget(self.embed_text_input)

        self.paste_button = QPushButton("Paste")
        self.paste_button.clicked.connect(self._paste_text)
        embed_text_layout.addWidget(self.paste_button)
        layout.addLayout(embed_text_layout)
        
        self.status_label = QLabel("Config Status:")
        layout.addWidget(self.status_label)
        
        self.status_bar = QWidget()
        self.status_bar.setFixedHeight(20) # set fixed height
        self._set_status_bar_color("red") # default color for json status
        layout.addWidget(self.status_bar)
        
        self._init_buttons(layout) # initialise buttons

    def _init_buttons(self, layout):
        config_button_layout = QHBoxLayout() # horizontal layout for config buttons
        
        self.load_config_button = QPushButton("Load Config")
        self.load_config_button.setToolTip("Load a configuration.")
        self.load_config_button.clicked.connect(self._load_config)
        config_button_layout.addWidget(self.load_config_button)

        self.unload_config_button = QPushButton("Unload Config")
        self.unload_config_button.setToolTip("Unload the current configuration.")
        self.unload_config_button.clicked.connect(self._unload_config)
        config_button_layout.addWidget(self.unload_config_button)
        layout.addLayout(config_button_layout)

        self.save_button = QPushButton("Save Stego Image")
        self.save_button.setToolTip("Save the stego image.")
        self.save_button.clicked.connect(self._save_stego_image)
        layout.addWidget(self.save_button)

        self.go_button = QPushButton("Go") # go button
        self.go_button.setToolTip("Start the embedding process.")
        self.go_button.clicked.connect(self._embed_data)
        layout.addWidget(self.go_button)

    def _load_config(self):
        try:
            file_path, _ = QFileDialog.getOpenFileName(self, "Select Config File", "", "JSON Files (*.json);;All Files (*)")
            if file_path:
                config = Steganography.load_config(file_path) # load config file
                if self._validate_config(config): # validate config
                    self.steganography = Steganography(config)
                    self._set_status_bar_color("green") # set status bar color to green
                    self.status_label.setText("Config Status: Loaded")
                else: # if validation fails
                    self._set_status_bar_color("orange")
                    self.status_label.setText("Config Status: Invalid")
                    self._show_error_message("Invalid configuration file.")
            else: # if no file selected
                self.status_label.setText("Failed to load config.")
        except Exception as e:
            self._show_error_message(f"Error loading config: {e}.\nMake sure the file is a valid JSON file.")

    def _validate_config(self, config):
        # required confg checks
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
        self.steganography = None # set steganography object to None to unload config
        self._set_status_bar_color("red") # set status bar color to red
        self.status_label.setText("Config Status: Unloaded")

    def _set_status_bar_color(self, color):
        palette = self.status_bar.palette() # get palette
        palette.setColor(QPalette.ColorRole.Window, QColor(color)) # set color
        self.status_bar.setAutoFillBackground(True) # set auto fill background
        self.status_bar.setPalette(palette) # set palette

    def _browse_image(self):
        try:
            file_path, _ = QFileDialog.getOpenFileName(self, "Select Image", "", "Images (*.png *.jpg *.bmp)") # filter file directory by image files
            if file_path:
                self.image_path.setText(file_path) # set image path in input field
                pixmap = QPixmap(file_path) # create pixmap from image
                self.original_scene.addPixmap(pixmap) # add pixmap to scene
        except Exception as e:
            self._show_error_message(f"Error browsing image: {e}.\nMake sure the file is an image.")

    def _save_stego_image(self):
        try:
            file_path, _ = QFileDialog.getSaveFileName(self, "Save Stego Image", "", "Images (*.png *.jpg *.bmp)")
            if file_path and self.steganography:
                image_path = self.image_path.text() # get image path
                text = self.embed_text_input.text() # get text to embed
                stego_image = self.steganography.embed_text(image_path, text) # embed text in image
                self.steganography.save_image(stego_image, file_path) # save stego image
                pixmap = QPixmap(file_path) # create pixmap from stego image
                self.stego_scene.addPixmap(pixmap) # add pixmap to scene
        except Exception as e:
            self._show_error_message(f"Error saving stego image: {e}.\nMake sure the file path is valid.")

    def _embed_data(self):
        try: # try embedding data
            if self.steganography:
                image_path = self.image_path.text()
                text = self.embed_text_input.text()
                stego_image = self.steganography.embed_text(image_path, text)
                self.stego_scene.clear() # clear scene
                stego_qimage = ImageQt(stego_image.convert("RGBA")) # convert image to RGBA
                stego_pixmap = QPixmap.fromImage(stego_qimage) # create pixmap from image
                self.stego_scene.addPixmap(stego_pixmap) # add pixmap to scene
        except Exception as e:
            self._show_error_message(f"Error embedding data: {e}.\nMake sure your config file is correct.")

    def _paste_text(self):
        clipboard_text = pyperclip.paste() # get text from clipboard
        current_text = self.embed_text_input.text() # get current text in input field
        self.embed_text_input.setText(current_text + clipboard_text) # append clipboard text to input field

    def _show_error_message(self, message):
        error_dialog = QMessageBox()
        error_dialog.setIcon(QMessageBox.Icon.Critical)
        error_dialog.setText(message)
        error_dialog.setWindowTitle("Error")
        error_dialog.exec()

class ZoomableGraphicsView(QGraphicsView):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag) # set drag mode to scroll hand drag
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse) # set transformation anchor to under mouse
        self.companion_view = None  # reference to the companion view for syncing
        self._is_syncing = False    # flag to prevent infinite recursion

    def wheelEvent(self, event: QWheelEvent): # method to handle wheel events
        if self._is_syncing:  # prevent infinite recursion
            return
            
        zoom_in_factor = 1.25
        zoom_out_factor = 1 / zoom_in_factor

        zoom_factor = zoom_in_factor if event.angleDelta().y() > 0 else zoom_out_factor # set zoom factor based on wheel direction
        
        self.scale(zoom_factor, zoom_factor) # apply zoom to self
        
        if self.companion_view and not self._is_syncing: # sync zoom with companion view
            self._is_syncing = True
            self.companion_view.setTransform(self.transform())
            self._is_syncing = False

    def scrollContentsBy(self, dx, dy):
        super().scrollContentsBy(dx, dy)

        if self.companion_view and not self._is_syncing: # sync scrolling with companion view
            self._is_syncing = True
            self.companion_view.horizontalScrollBar().setValue(self.horizontalScrollBar().value())
            self.companion_view.verticalScrollBar().setValue(self.verticalScrollBar().value())
            self._is_syncing = False