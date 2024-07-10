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
network_clock/
├── .gitignore
├── README.md
├── requirements.txt
├── config/
│   └── port.txt
├── src/
│   ├── __init__.py
│   ├── sh.py         # Main program (Standard Handler)
│   ├── ts.py         # Time setting program (Time Setup)
│   ├── ui.py         # User Interface
│   ├── server.py     # TCP server code
│   └── utils.py      # Utility functions
└── tests/
    ├── __init__.py
    ├── test_sh.py
    ├── test_ts.py
    ├── test_server.py
    └── test_utils.py

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