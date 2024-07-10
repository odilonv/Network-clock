# Network Clock

## Description
Network Clock (NC) is an application that displays the current time and responds to date/time requests via a TCP server. The local user can specify the exact format of the displayed value interactively, while remote users can request the current date and time in a specified format.

## Features
- **Local User Interface**: Allows the user to display the current time in a specified format.
- **TCP Server**: Responds to remote requests for the current date/time.
- **Privilege Separation**: A separate program (`ts.py`) with elevated privileges to set the system time.

## Installation
1. Clone this repository:
```bash
git clone https://github.com/odilonv/Network-clock.git
cd network_clock
```

2. Create and activate a virtual environment:
```bash
python -m venv env
source env/bin/activate  # On Windows: env\Scripts\activate
```

3. Install the dependencies:
```bash
pip install -r requirements.txt
```

4. Configure the TCP server port in config/port.txt.

## Usage
- To run the main program:
```bash
python src/sh.py
```

- To set the system time (requires elevated privileges):
```bash
python src/ts.py HH:MM:SS
```

## Directory Structure
`Network_clock/` <br>
├── `.gitignore` <br>
├── `README.md` <br>
├── `requirements.txt` <br>
├── `config/` <br>
│   └── `port.txt` <br>
├── `src/` <br>
│   ├── `__init__.py` <br>
│   ├── `sh.py`         # Main program (Standard Handler) <br>
│   ├── `ts.py`         # Time setting program (Time Setup) <br>
│   ├── `ui.py`         # User Interface <br>
│   ├── `server.py`     # TCP server code <br>
│   └── `utils.py`      # Utility functions <br>
└── `tests/` <br>
    ├── `__init__.py` <br>
    ├── `test_sh.py` <br>
    ├── `test_ts.py` <br>
    ├── `test_server.py` <br>
    └── `test_utils.py` <br>

## Configuration
- **TCP Server Port**: Set the desired port number in config/port.txt.

## Security Considerations
- The application follows the principle of least privilege.
- The ts.py script should be executed with elevated privileges for setting the system time.
- Input validation is implemented to prevent common vulnerabilities such as buffer overflows and format string exploits.

## Testing
To run the tests:
```bash
pytest tests/
```

## License
This project is licensed under the MIT License - see the LICENSE file for details.