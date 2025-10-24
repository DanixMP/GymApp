import jdatetime
from datetime import datetime

def gregorian_to_jalali(date_str):
    """Convert a Gregorian date string to Jalali date string."""
    if not date_str:
        return None
    try:
        # Parse the Gregorian date string
        if isinstance(date_str, str):
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
        else:
            date_obj = date_str
        # Convert to Jalali
        jalali_date = jdatetime.date.fromgregorian(date=date_obj.date())
        return jalali_date.strftime("%Y/%m/%d")
    except Exception:
        return None

def jalali_to_gregorian(jalali_date_str):
    """Convert a Jalali date string to Gregorian date string."""
    if not jalali_date_str:
        return None
    try:
        # Parse the Jalali date string
        jalali_date = jdatetime.datetime.strptime(jalali_date_str, "%Y/%m/%d").togregorian()
        return jalali_date.strftime("%Y-%m-%d")
    except Exception:
        return None

def get_current_jalali_date():
    """Get current date in Jalali format."""
    return jdatetime.datetime.now().strftime("%Y/%m/%d")

def format_jalali_date(date_str):
    """Format a date string for display in Persian."""
    if not date_str:
        return "تاریخ نامشخص"
    try:
        if isinstance(date_str, str):
            # Try to parse as Gregorian first
            date_obj = datetime.strptime(date_str, "%Y-%m-%d")
            jalali_date = jdatetime.date.fromgregorian(date=date_obj.date())
        else:
            # If it's already a datetime object
            jalali_date = jdatetime.date.fromgregorian(date=date_str.date())
        
        # Format with Persian month names
        months = {
            1: "فروردین",
            2: "اردیبهشت",
            3: "خرداد",
            4: "تیر",
            5: "مرداد",
            6: "شهریور",
            7: "مهر",
            8: "آبان",
            9: "آذر",
            10: "دی",
            11: "بهمن",
            12: "اسفند"
        }
        return f"{jalali_date.day} {months[jalali_date.month]} {jalali_date.year}"
    except Exception:
        return "تاریخ نامشخص"
