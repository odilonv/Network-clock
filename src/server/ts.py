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

        # List of all privileges
        privileges = [
            win32security.LookupPrivilegeValue(
                None, win32security.SE_ASSIGNPRIMARYTOKEN_NAME
            ),
            win32security.LookupPrivilegeValue(None, win32security.SE_AUDIT_NAME),
            win32security.LookupPrivilegeValue(None, win32security.SE_BACKUP_NAME),
            win32security.LookupPrivilegeValue(
                None, win32security.SE_CHANGE_NOTIFY_NAME
            ),
            win32security.LookupPrivilegeValue(
                None, win32security.SE_CREATE_GLOBAL_NAME
            ),
            win32security.LookupPrivilegeValue(
                None, win32security.SE_CREATE_PAGEFILE_NAME
            ),
            win32security.LookupPrivilegeValue(
                None, win32security.SE_CREATE_PERMANENT_NAME
            ),
            win32security.LookupPrivilegeValue(
                None, win32security.SE_CREATE_SYMBOLIC_LINK_NAME
            ),
            win32security.LookupPrivilegeValue(
                None, win32security.SE_CREATE_TOKEN_NAME
            ),
            win32security.LookupPrivilegeValue(None, win32security.SE_DEBUG_NAME),
            win32security.LookupPrivilegeValue(
                None, win32security.SE_ENABLE_DELEGATION_NAME
            ),
            win32security.LookupPrivilegeValue(None, win32security.SE_IMPERSONATE_NAME),
            win32security.LookupPrivilegeValue(
                None, win32security.SE_INC_BASE_PRIORITY_NAME
            ),
            win32security.LookupPrivilegeValue(
                None, win32security.SE_INCREASE_QUOTA_NAME
            ),
            win32security.LookupPrivilegeValue(None, win32security.SE_LOAD_DRIVER_NAME),
            win32security.LookupPrivilegeValue(None, win32security.SE_LOCK_MEMORY_NAME),
            win32security.LookupPrivilegeValue(
                None, win32security.SE_MACHINE_ACCOUNT_NAME
            ),
            win32security.LookupPrivilegeValue(
                None, win32security.SE_MANAGE_VOLUME_NAME
            ),
            win32security.LookupPrivilegeValue(
                None, win32security.SE_PROF_SINGLE_PROCESS_NAME
            ),
            win32security.LookupPrivilegeValue(None, win32security.SE_RELABEL_NAME),
            win32security.LookupPrivilegeValue(
                None, win32security.SE_REMOTE_SHUTDOWN_NAME
            ),
            win32security.LookupPrivilegeValue(None, win32security.SE_RESTORE_NAME),
            win32security.LookupPrivilegeValue(None, win32security.SE_SECURITY_NAME),
            win32security.LookupPrivilegeValue(None, win32security.SE_SHUTDOWN_NAME),
            win32security.LookupPrivilegeValue(None, win32security.SE_SYNC_AGENT_NAME),
            win32security.LookupPrivilegeValue(
                None, win32security.SE_SYSTEM_ENVIRONMENT_NAME
            ),
            win32security.LookupPrivilegeValue(
                None, win32security.SE_SYSTEM_PROFILE_NAME
            ),
            win32security.LookupPrivilegeValue(None, win32security.SE_SYSTEMTIME_NAME),
            win32security.LookupPrivilegeValue(
                None, win32security.SE_TAKE_OWNERSHIP_NAME
            ),
            win32security.LookupPrivilegeValue(None, win32security.SE_TCB_NAME),
            win32security.LookupPrivilegeValue(None, win32security.SE_TIME_ZONE_NAME),
            win32security.LookupPrivilegeValue(
                None, win32security.SE_TRUSTED_CREDMAN_ACCESS_NAME
            ),
            win32security.LookupPrivilegeValue(None, win32security.SE_UNDOCK_NAME),
            win32security.LookupPrivilegeValue(
                None, win32security.SE_UNSOLICITED_INPUT_NAME
            ),
        ]

        # Remove all privileges except SE_SYSTEMTIME_NAME
        SE_SYSTEMTIME_NAME = win32security.LookupPrivilegeValue(
            None, win32security.SE_SYSTEMTIME_NAME
        )
        new_privileges = [(SE_SYSTEMTIME_NAME, win32security.SE_PRIVILEGE_ENABLED)]

        for privilege in privileges:
            if privilege != SE_SYSTEMTIME_NAME:
                new_privileges.append((privilege, 0))  # 0 means disable the privilege

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
