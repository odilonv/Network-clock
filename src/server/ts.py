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
    except Exception:
        pass


def drop_privileges():
    try:
        current_process = win32api.GetCurrentProcess()
        token = win32security.OpenProcessToken(
            current_process,
            win32security.TOKEN_ADJUST_PRIVILEGES | win32security.TOKEN_QUERY,
        )

        privilege_names = [
            win32security.LookupPrivilegeName(None, privilege[0])
            for privilege in win32security.GetTokenInformation(
                token, win32security.TokenPrivileges
            )
        ]
        unnecessary_privileges = [
            win32security.LookupPrivilegeValue(None, privilege)
            for privilege in privilege_names
            if privilege != win32security.SE_SYSTEMTIME_NAME
        ]

        new_privileges = [
            (privilege, win32security.SE_PRIVILEGE_REMOVED)
            for privilege in unnecessary_privileges
        ]
        win32security.AdjustTokenPrivileges(token, False, new_privileges)

        se_systemtime_privilege = [
            (
                win32security.LookupPrivilegeValue(
                    None, win32security.SE_SYSTEMTIME_NAME
                ),
                win32security.SE_PRIVILEGE_ENABLED,
            )
        ]
        win32security.AdjustTokenPrivileges(token, False, se_systemtime_privilege)

    except Exception:
        pass


def set_system_time(date_str, time_str):
    try:
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

        if not SetLocalTime(ctypes.byref(st)):
            pass
    except ValueError:
        pass


if __name__ == "__main__":
    subscribe_to_dep()
    drop_privileges()

    date_str = sys.argv[1]
    time_str = sys.argv[2]
    set_system_time(date_str, time_str)
