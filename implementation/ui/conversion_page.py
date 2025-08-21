from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QProgressBar, QFileDialog, QCheckBox, QSpinBox
from PIL import Image
import os
from data_structures.linkedlist import LinkedList

class ConversionPage(QWidget):
    def __init__(self):
        super().__init__()
        self._init_ui()
        self._task_list = LinkedList()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        
        self._convert_label = QLabel("Select image(s) to convert:")  # image selection label
        layout.addWidget(self._convert_label) # add label to layout
        
        self._convert_path = QLineEdit()  # image path input field
        self._convert_path.setToolTip("Path to the image(s) to be converted.")
        layout.addWidget(self._convert_path)
        
        self._convert_browse_button = QPushButton("Browse")  # browse for images button
        self._convert_browse_button.setToolTip("Browse and select image(s) to convert.") # tooltip for browse button
        self._convert_browse_button.clicked.connect(self._browse_images) # connect browse button to browse_images method
        layout.addWidget(self._convert_browse_button)
        
        self._batch_convert_checkbox = QCheckBox("Convert all images in directory")  # batch conversion checkbox
        self._batch_convert_checkbox.setToolTip("Check to convert all images in the selected directory.")
        layout.addWidget(self._batch_convert_checkbox)
        
        self._output_dir_label = QLabel("Select output directory:")
        layout.addWidget(self._output_dir_label)
        
        self._output_dir_path = QLineEdit()
        self._output_dir_path.setToolTip("Path to the directory where converted images will be saved.")
        layout.addWidget(self._output_dir_path)
        
        self._output_dir_browse_button = QPushButton("Browse")
        self._output_dir_browse_button.setToolTip("Browse and select the output directory.")
        self._output_dir_browse_button.clicked.connect(self._browse_output_directory)
        layout.addWidget(self._output_dir_browse_button)
        
        self._extension_label = QLabel("Select output format:")
        layout.addWidget(self._extension_label)
        
        self._extension_dropdown = QComboBox()  # output format dropdown
        self._extension_dropdown.addItems([".png", ".jpg", ".bmp"]) # add items to dropdown
        self._extension_dropdown.setToolTip("Select the output format for the converted images.")
        self._extension_dropdown.currentIndexChanged.connect(self._toggle_quality_options) # connect to method to toggle quality options
        layout.addWidget(self._extension_dropdown)
        
        self._quality_label = QLabel("Set image quality (1-100):")
        layout.addWidget(self._quality_label)
        
        self._quality_spinbox = QSpinBox()  # image quality spinbox
        self._quality_spinbox.setRange(1, 100) # spinbox range
        self._quality_spinbox.setValue(90) # set default value
        self._quality_spinbox.setToolTip("Set the quality of .jpg output images (1-100).")
        layout.addWidget(self._quality_spinbox)
        
        self._overwrite_checkbox = QCheckBox("Overwrite existing files")
        self._overwrite_checkbox.setToolTip("Check to overwrite existing files in the output directory.")
        layout.addWidget(self._overwrite_checkbox)
        
        self._resize_checkbox = QCheckBox("Resize images")
        self._resize_checkbox.setToolTip("Check to resize the images during conversion.")
        self._resize_checkbox.stateChanged.connect(self._toggle_resize_options)
        layout.addWidget(self._resize_checkbox)
        
        self._resize_width_label = QLabel("Width:")
        self._resize_width_label.setEnabled(False) # disable width label by default
        layout.addWidget(self._resize_width_label)
        
        self._resize_width_spinbox = QSpinBox()
        self._resize_width_spinbox.setRange(1, 10000)
        self._resize_width_spinbox.setEnabled(False) # disable width spinbox by default
        self._resize_width_spinbox.setToolTip("Set the width for resizing the images.")
        layout.addWidget(self._resize_width_spinbox)
        
        self._resize_height_label = QLabel("Height:")
        self._resize_height_label.setEnabled(False)
        layout.addWidget(self._resize_height_label)
        
        self._resize_height_spinbox = QSpinBox()
        self._resize_height_spinbox.setRange(1, 10000)
        self._resize_height_spinbox.setEnabled(False)
        self._resize_height_spinbox.setToolTip("Set the height for resizing the images.")
        layout.addWidget(self._resize_height_spinbox)
        
        self._maintain_aspect_ratio_checkbox = QCheckBox("Maintain aspect ratio")
        self._maintain_aspect_ratio_checkbox.setEnabled(False)
        self._maintain_aspect_ratio_checkbox.setToolTip("Check to maintain the aspect ratio when resizing images.")
        layout.addWidget(self._maintain_aspect_ratio_checkbox)
        
        self._convert_button = QPushButton("Convert")
        self._convert_button.setToolTip("Start the conversion process.")
        self._convert_button.clicked.connect(self._convert_images)
        layout.addWidget(self._convert_button)
        
        self._progress_bar = QProgressBar()  # conversion progress bar
        layout.addWidget(self._progress_bar)
        
        self._status_label = QLabel("Status: Ready")
        layout.addWidget(self._status_label)

        self._toggle_quality_options()  # initial call to set visibility based on default selection

    def _browse_images(self):
        if self._batch_convert_checkbox.isChecked():
            dir_dialog = QFileDialog() # directory dialog
            directory = dir_dialog.getExistingDirectory(self, "Select Directory")
            if directory:
                self._convert_path.setText(directory) # set directory path in input field
        else:
            file_dialog = QFileDialog() # file dialog
            file_paths, _ = file_dialog.getOpenFileNames(self, "Select Images", "", "Images (*.png *.jpg *.bmp)") # get file paths
            if file_paths:
                self._convert_path.setText("; ".join(file_paths)) # set file paths in input field, joined by "; " in order to separate multiple paths

    def _browse_output_directory(self):
        dir_dialog = QFileDialog()
        output_dir = dir_dialog.getExistingDirectory(self, "Select Output Directory")
        if output_dir:
            self._output_dir_path.setText(output_dir) # set output directory path in input field if it exists

    def _toggle_resize_options(self): # method to enable/disable resize options based on checkbox state
        enabled = self._resize_checkbox.isChecked()
        self._resize_width_label.setEnabled(enabled)
        self._resize_width_spinbox.setEnabled(enabled)
        self._resize_height_label.setEnabled(enabled)
        self._resize_height_spinbox.setEnabled(enabled)
        self._maintain_aspect_ratio_checkbox.setEnabled(enabled)

    def _toggle_quality_options(self): # method to show/hide quality options based on output format
        is_jpg = self._extension_dropdown.currentText() == ".jpg"
        self._quality_label.setVisible(is_jpg)
        self._quality_spinbox.setVisible(is_jpg)

    def _convert_images(self): # method to convert images
        try:
            file_paths = self._get_file_paths()
        except (FileNotFoundError, NotADirectoryError) as e:
            self._status_label.setText(str(e))
            return
        output_dir = self._output_dir_path.text()
        if not os.path.isdir(output_dir):
            self._status_label.setText(f"The output directory does not exist: '{output_dir}'")
            return
        file_paths = self._merge_sort(file_paths)  # sort file paths using Mergesort
        output_format = self._extension_dropdown.currentText()
        quality = self._quality_spinbox.value()
        overwrite = self._overwrite_checkbox.isChecked()
        resize = self._resize_checkbox.isChecked()
        maintain_aspect_ratio = self._maintain_aspect_ratio_checkbox.isChecked()
        width = self._resize_width_spinbox.value()
        height = self._resize_height_spinbox.value()
        total_files = len(file_paths) # total number of files to convert
        
        # Add tasks to the linked list
        for file_path in file_paths:
            self._task_list.append((file_path, output_format, output_dir, quality, overwrite, resize, maintain_aspect_ratio, width, height))

        # Process tasks from the linked list
        while not self._task_list.is_empty():
            task = self._task_list.pop()
            try:
                self._process_image(*task)
            except Exception as e:
                self._status_label.setText(f"Error converting {task[0]}: {e}")
                return

            self._progress_bar.setValue(int((total_files - self._task_list_length()) / total_files * 100)) # update progress bar
            self._status_label.setText(f"Converting {total_files - self._task_list_length()}/{total_files} images...") # update status label

        self._status_label.setText("Conversion complete!")

    def _task_list_length(self):
        return self._task_list.length()

    def _get_file_paths(self):
        path = self._convert_path.text()
        if not path:
            raise ValueError("No file or directory selected")
            
        if self._batch_convert_checkbox.isChecked():
            # handle batch conversion from directory
            if os.path.isfile(path):
                path = os.path.dirname(path)  # convert file path to directory path
            if not os.path.isdir(path):
                raise NotADirectoryError(f"The directory does not exist: '{path}'")
            return [os.path.join(path, file_name) 
                   for file_name in os.listdir(path) 
                   if file_name.lower().endswith(('.png', '.jpg', '.bmp'))]
        else:
            # handle single or multiple file selection
            file_paths = [p.strip() for p in path.split(";") if p.strip()]
            for file_path in file_paths:
                if not os.path.isfile(file_path):
                    raise FileNotFoundError(f"The file does not exist: '{file_path}'")
            return file_paths

    def _process_image(self, file_path, output_format, output_dir, quality, overwrite, resize, maintain_aspect_ratio, width, height):
        img = Image.open(file_path)
        if resize:
            img = self._resize_image(img, maintain_aspect_ratio, width, height) # resize image
        if output_format == ".jpg" and img.mode == "RGBA": # convert RGBA to RGB for .jpg format
            img = img.convert("RGB") # convert img to RGB mode
        output_path = self._get_output_path(file_path, output_format, output_dir, overwrite)
        try:
            with open(output_path, 'wb') as f:  # ensure the file can be opened for writing
                if output_format == ".jpg":
                    img.save(f, format="JPEG", quality=quality) # save with specified quality for JPEG
                else:
                    img.save(f, format=output_format[1:].upper()) # save without quality for other formats
        except Exception as e:
            self._status_label.setText(f"Error saving {output_path}: {e}")
            raise

    def _resize_image(self, img, maintain_aspect_ratio, width, height):
        if maintain_aspect_ratio:
            img.thumbnail((width, height)) # resize  while maintaining aspect ratio
        else:
            img = img.resize((width, height)) # resize without maintaining aspect ratio
        return img

    def _get_output_path(self, file_path, output_format, output_dir, overwrite):
        output_path = os.path.join(output_dir, os.path.basename(file_path).rsplit('.', 1)[0] + output_format) # create output path
        if not output_path:
            raise ValueError("Output directory is invalid")
        if not overwrite and os.path.exists(output_path):
            base, ext = os.path.splitext(output_path) # split path into base and extension
            counter = 1
            while os.path.exists(output_path):
                output_path = f"{base}_{counter}{ext}" # add counter to filename if file already exists
                counter += 1
        return output_path

    def _merge_sort(self, file_paths):
        if len(file_paths) <= 1:
            return file_paths
        mid = len(file_paths) // 2 # find middle index
        left_half = self._merge_sort(file_paths[:mid]) # recursively sort left half
        right_half = self._merge_sort(file_paths[mid:]) # recursively sort right half
        return self._merge(left_half, right_half)

    def _merge(self, left, right):
        sorted_list = []
        while left and right:
            if left[0] <= right[0]: # compare first elements of left and right lists
                sorted_list.append(left.pop(0)) # remove first element from left list and append to sorted list
            else:
                sorted_list.append(right.pop(0))
        sorted_list.extend(left or right) # extend sorted list with remaining elements from left or right list
        return sorted_list