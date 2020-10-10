import sys
import subprocess
import ctypes
from datetime import datetime


def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False


def set_system_time(date_str, time_str):
    try:
        new_time = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")

        SYSTEMTIME = ctypes.c_uint16 * 8
        st = SYSTEMTIME(
            new_time.year,
            new_time.month,
            new_time.weekday(),
            new_time.day,
            new_time.hour,
            new_time.minute,
            new_time.second,
            0,
        )

        SetLocalTime = ctypes.windll.kernel32.SetLocalTime
        SetLocalTime.argtypes = [ctypes.POINTER(SYSTEMTIME)]
        SetLocalTime.restype = ctypes.c_bool

        if SetLocalTime(ctypes.byref(st)):
            error_code = ctypes.windll.kernel32.GetLastError()
            return f"Failed to set system time. Error code: {error_code}"
        else:
            return "System time has been updated successfully."

    except ValueError:
        return "Invalid datetime format. Please use YYYY-MM-DD HH:MM:SS"
    except Exception as e:
        return f"Error: {e}"


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python ts.py <date> <time>")
        sys.exit(1)

    date = sys.argv[1]
    time = sys.argv[2]

    if not is_admin():
        try:
            script_path = sys.argv[0]
            powershell_cmd = [
                "powershell.exe",
                "-Command",
                f"Start-Process python -ArgumentList '{script_path}', '{date}', '{time}' -Verb RunAs",
            ]
            subprocess.check_call(" ".join(powershell_cmd), shell=True)
        except subprocess.CalledProcessError as e:
            print(f"Failed to run script as admin: {e}")
            sys.exit(1)

    result = set_system_time(date, time)
    print(result)
