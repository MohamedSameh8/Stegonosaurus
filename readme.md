# Stegonosaurus: Image Steganography & Encryption

## Overview
Stegonosaurus is a Python application that combines steganography, encryption, and noise-based techniques to conceal and protect data within images. It features a Qt-based GUI for configuring parameters, encoding, decoding, and previewing results.

## Features
- Multiple encoding methods: AES-encrypted payloads, noise injection, PVD, and XSB.
- User-friendly interface built with PyQt6.
- Customisable configuration via JSON files.
- Data structures optimised for payload handling.

## Installation
1. Clone the repository:
	```powershell
	git clone https://github.com/xathail/NEA.git
	cd NEA/implementation
	```
2. Create and activate a virtual environment:
	```powershell
	python -m venv venv; .\venv\Scripts\Activate.ps1
	```
3. Install dependencies:
	```powershell
	pip install -r requirements.txt
	```

## Usage
Run the main application:
```powershell
python main.py
```
Navigate through the tabs to set up encoding or decoding parameters and start the process.

## Configuration
Configuration is managed from within the application’s “Config” tab:
- Adjust algorithm parameters, encryption keys, and noise settings interactively.
- Click **Save Config** to export your settings as a JSON file.
- Use **Load Config** to re-import a saved configuration.

## Project Structure
```
implementation/          Main logic and GUI entry point
├── ui/                  PyQt6 interface modules
├── enc/                 Encryption and noise routines
├── meth/                Steganography algorithms (PVD & XSB)
├── data_structures/     Helper structures (hashtable, linkedlist)
└── test/                Unit tests and sample data
```

## Contributing
Contributions are welcome. Please open issues or pull requests to report bugs or suggest features. Ensure new code follows existing style and adds corresponding tests.

## License
Licensed under the MIT License.
