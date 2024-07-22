import sys
import ctypes
from datetime import datetime
import os
import win32api
import win32security


def subscribe_to_dep():
    try:
        if os.name == "nt":
            ctypes.windll.kernel32.SetProcessDEPPolicy(1)
    except Exception as e:
        print(f"Error subscribing to DEP: {e}")


def drop_privileges():
    try:
        # On Windows, create a restricted token
        current_process = win32api.GetCurrentProcess()
        token = win32security.OpenProcessToken(
            current_process,
            win32security.TOKEN_ADJUST_PRIVILEGES | win32security.TOKEN_QUERY,
        )

        # Get the current privileges
        current_privileges = win32security.GetTokenInformation(
            token, win32security.TokenPrivileges
        )

        # New privileges list: disable all privileges
        new_privileges = [
            (privilege, 0) for privilege, attributes in current_privileges
        ]

        win32security.AdjustTokenPrivileges(token, False, new_privileges)
    except Exception as e:
        print(f"Error dropping privileges: {e}")


def set_system_time(date_str, time_str):
    try:
        print(f"Received date: {date_str}, time: {time_str}")
        new_time = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M:%S")

        class SYSTEMTIME(ctypes.Structure):
            _fields_ = [
                ("wYear", ctypes.c_ushort),
                ("wMonth", ctypes.c_ushort),
                ("wDayOfWeek", ctypes.c_ushort),
                ("wDay", ctypes.c_ushort),
                ("wHour", ctypes.c_ushort),
                ("wMinute", ctypes.c_ushort),
                ("wSecond", ctypes.c_ushort),
                ("wMilliseconds", ctypes.c_ushort),
            ]

        st = SYSTEMTIME(
            wYear=new_time.year,
            wMonth=new_time.month,
            wDayOfWeek=new_time.weekday(),
            wDay=new_time.day,
            wHour=new_time.hour,
            wMinute=new_time.minute,
            wSecond=new_time.second,
            wMilliseconds=0,
        )

        SetLocalTime = ctypes.windll.kernel32.SetLocalTime
        SetLocalTime.argtypes = [ctypes.POINTER(SYSTEMTIME)]
        SetLocalTime.restype = ctypes.c_bool

        # Set the system time using the new time
        if not SetLocalTime(ctypes.byref(st)):
            print("Failed to set system time.")
    except ValueError:
        print("Invalid datetime format. Please use YYYY-MM-DD HH:MM:SS")


if __name__ == "__main__":
    subscribe_to_dep()
    drop_privileges()

    date_str = sys.argv[1]
    time_str = sys.argv[2]
    set_system_time(date_str, time_str)
