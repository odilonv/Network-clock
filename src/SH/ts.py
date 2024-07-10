import sys
import ctypes
import datetime
import pytz

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin() != 0
    except:
        return False

def set_system_time(new_time_str):
    try:
        # Conversion de la chaîne de temps en objet datetime
        new_time = datetime.datetime.strptime(new_time_str, '%Y-%m-%d %H:%M:%S')

        # Convertir en UTC pour éviter les problèmes de fuseau horair   e
        new_time_utc = pytz.utc.localize(new_time)

        # Définition de la structure SYSTEMTIME
        class SYSTEMTIME(ctypes.Structure):
            _fields_ = [
                ("wYear", ctypes.c_ushort),
                ("wMonth", ctypes.c_ushort),
                ("wDayOfWeek", ctypes.c_ushort),
                ("wDay", ctypes.c_ushort),
                ("wHour", ctypes.c_ushort),
                ("wMinute", ctypes.c_ushort),
                ("wSecond", ctypes.c_ushort),
                ("wMilliseconds", ctypes.c_ushort)
            ]

        # Création d'une instance de SYSTEMTIME
        system_time = SYSTEMTIME(
            wYear=new_time_utc.year,
            wMonth=new_time_utc.month,
            wDayOfWeek=new_time_utc.weekday(),
            wDay=new_time_utc.day,
            wHour=new_time_utc.hour,
            wMinute=new_time_utc.minute,
            wSecond=new_time_utc.second,
            wMilliseconds=new_time_utc.microsecond // 1000
        )

        # Appel à l'API Windows pour changer l'heure système
        success = ctypes.windll.kernel32.SetSystemTime(ctypes.byref(system_time))
        if success == 0:
            return f"Failed to set system time. Error code: {ctypes.windll.kernel32.GetLastError()}"
        else:
            return "System time has been updated successfully."

    except ValueError:
        return "Invalid datetime format. Please use YYYY-MM-DD HH:MM:SS"
    except Exception as e:
        return f"Error: {e}"

if __name__ == '__main__':
    if not is_admin():
        # Relancer le script avec des privilèges administratifs si nécessaire
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
    elif len(sys.argv) < 2:
        print("Usage: python ts.py <new_time>")
    else:
        new_time = sys.argv[1]
        result = set_system_time(new_time)
        print(result)
