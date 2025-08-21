from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QLineEdit, QPushButton, QSlider, QFileDialog, QMessageBox, QHBoxLayout, QTextEdit
from PyQt6.QtCore import Qt
import json
import pyperclip
import os

class ConfigPage(QWidget):
    def __init__(self):
        super().__init__()
        layout = QHBoxLayout(self)

        self.options_layout = QVBoxLayout() # vertical layout for options
        self.json_layout = QVBoxLayout() # vertical layout for json display

        self.algorithm_label = QLabel("Choice of algorithm:") # algorithm selection label
        self.options_layout.addWidget(self.algorithm_label) # add label to layout

        self.algorithm_dropdown = QComboBox() # algorithm selection dropdown
        self.algorithm_dropdown.addItems(["X Significant Bit", "Pixel Value Differencing"]) # add items to dropdown
        self.algorithm_dropdown.setToolTip("Select the algorithm for embedding data.")
        self.algorithm_dropdown.currentTextChanged.connect(self._update_json_display) # update json display on change
        self.algorithm_dropdown.currentTextChanged.connect(self._toggle_bit_position_fields) # connect dropdown to toggle_bit_position_fields method
        self.options_layout.addWidget(self.algorithm_dropdown)

        self.encryption_label = QLabel("Choice of encryption:")
        self.options_layout.addWidget(self.encryption_label)

        self.encryption_dropdown = QComboBox()
        self.encryption_dropdown.addItems(["None", "Base64", "AES"])
        self.encryption_dropdown.setToolTip("Select the encryption method for the data.")
        self.encryption_dropdown.currentTextChanged.connect(self._toggle_aes_fields)
        self.encryption_dropdown.currentTextChanged.connect(self._update_json_display)
        self.options_layout.addWidget(self.encryption_dropdown)

        self.aes_key_label = QLabel("AES Key (16 characters, leave blank for random):")
        self.aes_key_label.setVisible(False) # set visibility to false
        self.options_layout.addWidget(self.aes_key_label)

        self.aes_key_input = QLineEdit()
        self.aes_key_input.setMaxLength(16) # set max length
        self.aes_key_input.setVisible(False) # set visibility to false
        self.aes_key_input.setToolTip("Leave blank for random key")
        self.aes_key_input.textChanged.connect(self._update_json_display)
        self.options_layout.addWidget(self.aes_key_input)

        self.aes_iv_label = QLabel("AES IV (16 characters, leave blank for random):")
        self.aes_iv_label.setVisible(False) # set visibility to false
        self.options_layout.addWidget(self.aes_iv_label)

        self.aes_iv_input = QLineEdit()
        self.aes_iv_input.setMaxLength(16)
        self.aes_iv_input.setVisible(False)
        self.aes_iv_input.setToolTip("Leave blank for random IV")
        self.aes_iv_input.textChanged.connect(self._update_json_display)
        self.options_layout.addWidget(self.aes_iv_input)

        self.bit_position_label = QLabel("Bit Position:")
        self.bit_position_label.setVisible(False) # set visibility to false
        self.options_layout.addWidget(self.bit_position_label)

        self.bit_position_slider = QSlider(Qt.Orientation.Horizontal) # bit position slider
        self.bit_position_slider.setRange(1, 8) # set range
        self.bit_position_slider.setSingleStep(1) # set single step
        self.bit_position_slider.setValue(8) #  set default value
        self.bit_position_slider.setTickPosition(QSlider.TickPosition.TicksBelow) # set tick position
        self.bit_position_slider.setTickInterval(1) 
        self.bit_position_slider.setVisible(False)
        self.bit_position_slider.valueChanged.connect(self._update_json_display) # update json display on change
        self.options_layout.addWidget(self.bit_position_slider)

        bit_position_labels_layout = QHBoxLayout() # horizontal layout for bit position labels
        self.least_significant_label = QLabel("Least Significant")
        self.least_significant_label.setVisible(False)
        bit_position_labels_layout.addWidget(self.least_significant_label)

        bit_position_labels_layout.addStretch()

        self.most_significant_label = QLabel("Most Significant")
        self.most_significant_label.setVisible(False)
        bit_position_labels_layout.addWidget(self.most_significant_label)

        self.options_layout.addLayout(bit_position_labels_layout)

        self.algorithm_dropdown.setCurrentText("X Significant Bit")
        self._toggle_bit_position_fields("X Significant Bit")

        self.noise_level_label = QLabel("Noise Level:")
        self.options_layout.addWidget(self.noise_level_label)

        self.noise_level_slider = QSlider(Qt.Orientation.Horizontal)
        self.noise_level_slider.setRange(10, 100) # set range, actual value is divided by 10
        self.noise_level_slider.setSingleStep(1) # set single step
        self.noise_level_slider.setValue(10) # set default value
        self.noise_level_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.noise_level_slider.setTickInterval(10)
        self.noise_level_slider.valueChanged.connect(self._update_noise_level_label)
        self.noise_level_slider.valueChanged.connect(self._update_json_display)
        self.options_layout.addWidget(self.noise_level_slider)

        self.noise_level_value_label = QLabel("1.0") # noise level value label
        self.options_layout.addWidget(self.noise_level_value_label)

        self.save_config_button = QPushButton("Save Config")
        self.save_config_button.setToolTip("Save the current configuration.")
        self.save_config_button.clicked.connect(self._save_config)
        self.options_layout.addWidget(self.save_config_button)

        self.load_config_button = QPushButton("Load Config")
        self.load_config_button.setToolTip("Load a custom configuration.")
        self.load_config_button.clicked.connect(self._load_config)
        self.options_layout.addWidget(self.load_config_button)

        self.json_display = QTextEdit()
        self.json_display.setReadOnly(True)
        self.json_layout.addWidget(self.json_display)

        self.copy_button = QPushButton("Copy JSON")
        self.copy_button.setToolTip("Copy the JSON configuration to clipboard.")
        self.copy_button.clicked.connect(self._copy_json_to_clipboard)
        self.json_layout.addWidget(self.copy_button)

        layout.addLayout(self.options_layout)
        layout.addLayout(self.json_layout)

        self._update_json_display()

    def _toggle_aes_fields(self, encryption_type):
        is_aes = encryption_type == "AES"
        self.aes_key_label.setVisible(is_aes) # set visibility to is_aes (if encryption type is AES show key label)
        self.aes_key_input.setVisible(is_aes)
        self.aes_iv_label.setVisible(is_aes)
        self.aes_iv_input.setVisible(is_aes)

    def _toggle_bit_position_fields(self, algorithm_type):
        is_xsb = algorithm_type == "X Significant Bit"
        self.bit_position_label.setVisible(is_xsb) # set visibility to is_xsb (if algorithm type is XSB show bit position label)
        self.bit_position_slider.setVisible(is_xsb)
        self.least_significant_label.setVisible(is_xsb)
        self.most_significant_label.setVisible(is_xsb)

    def _update_noise_level_label(self, value):
        self.noise_level_value_label.setText(f"{value / 10:.1f}") # set noise level value label

    def _update_json_display(self):
        # create config dictionary
        config = {
            "algorithm": self.algorithm_dropdown.currentText(),
            "encryption": self.encryption_dropdown.currentText(),
            "noise_level": self.noise_level_slider.value() / 10
        }
        if self.encryption_dropdown.currentText() == "AES": # addd key and iv if AES
            config["key"] = self.aes_key_input.text()
            config["iv"] = self.aes_iv_input.text()
        if self.algorithm_dropdown.currentText() == "X Significant Bit": # add bit position if XSB
            config["bit_position"] = self.bit_position_slider.value()
        self.json_display.setText(json.dumps(config, indent=4))

    def _pad_string(self, text, target_length=16):
        # pad string to target length
        if not text:
            return ""
        return (text * ((target_length // len(text)) + 1))[:target_length]
    
    def _save_config(self):
        # save config to file
        self._update_json_display()
        config = json.loads(self.json_display.toPlainText())
    
        if config["encryption"] == "AES":
            key = config.get("key", "")
            iv = config.get("iv", "")
            
            key_modified = False
            iv_modified = False
            
            if not key:
                key = os.urandom(16).hex()[:16]
                key_modified = True
            elif len(key) != 16:
                key = self._pad_string(key)
                key_modified = True
                
            if not iv:
                iv = os.urandom(16).hex()[:16]
                iv_modified = True
            elif len(iv) != 16:
                iv = self._pad_string(iv)
                iv_modified = True
    
            if key_modified or iv_modified:
                message = []
                if key_modified:
                    message.append("Key was adjusted to 16 characters")
                    self.aes_key_input.setText(key)
                if iv_modified:
                    message.append("IV was adjusted to 16 characters")
                    self.aes_iv_input.setText(iv)
                    
                QMessageBox.information(
                    self,
                    "AES Parameters Adjusted",
                    "\n".join(message)
                )
                
            config["key"] = key
            config["iv"] = iv
            self._update_json_display()
    
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Config", "", "JSON Files (*.json);;All Files (*)")
        if file_name:
            with open(file_name, 'w') as file:
                json.dump(config, file)

    def _load_config(self):
        try:
            file_dialog = QFileDialog()
            file_path, _ = file_dialog.getOpenFileName(self, "Select Config File", "", "JSON Files (*.json);;All Files (*)")
            if file_path:
                with open(file_path, 'r') as file:
                    config = json.load(file)
                    if self._validate_config(config): # validate config
                        self.algorithm_dropdown.setCurrentText(config.get("algorithm", "Pixel Value Differencing")) # set values
                        self.encryption_dropdown.setCurrentText(config.get("encryption", "None"))
                        self.noise_level_slider.setValue(int(config.get("noise_level", 1.0) * 10))
                        if config.get("encryption") == "AES":
                            self.aes_key_input.setText(config.get("key", "")) # set key and iv
                            self.aes_iv_input.setText(config.get("iv", ""))
                        else:
                            self.aes_key_input.clear() # clear key and iv
                            self.aes_iv_input.clear()
                        if config.get("algorithm") == "X Significant Bit":
                            self.bit_position_slider.setValue(config.get("bit_position", 8)) # set bit position
                        self._update_json_display() # update json display with loaded config
                    else:
                        self._show_error_message("Invalid configuration file.")
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

    def _copy_json_to_clipboard(self):
        pyperclip.copy(self.json_display.toPlainText()) # copy json to clipboard

    def _show_error_message(self, message):
        error_dialog = QMessageBox()
        error_dialog.setIcon(QMessageBox.Icon.Critical)
        error_dialog.setText(message)
        error_dialog.setWindowTitle("Error")
        error_dialog.exec()