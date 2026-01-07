CATEGORIES = {
    "user_temp": {
        "label": "User Temp",
        "requires_admin": False,
        "note": "Safe cleanup of user temporary files",
    },
    "system_temp": {
        "label": "Windows Temp",
        "requires_admin": False,
        "note": "May require administrator privileges",
    },
    "recycle_bin": {
        "label": "Recycle Bin",
        "requires_admin": False,
        "note": "Deletes items from the Recycle Bin",
    },
    "dns_cache": {
        "label": "DNS cache",
        "requires_admin": True,
        "note": "Administrator privileges required",
    },
    "app_logs": {
        "label": "GreenBoost logs",
        "requires_admin": False,
        "note": "Removes old application logs",
    },
}

PROFILE_QUICK = ["user_temp", "system_temp", "app_logs"]
PROFILE_DEEP = ["user_temp", "system_temp", "recycle_bin", "dns_cache", "app_logs"]
