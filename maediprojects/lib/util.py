import datetime
import re


ALLOWED_YEARS = range(2013, datetime.datetime.utcnow().year+3)

MONTHS_QUARTERS = {
    1: 1, 2: 1, 3: 1, 4: 2, 5: 2, 6: 2, 7: 3, 8: 3, 9: 3, 10: 4, 
    11: 4, 12: 4
}

QUARTERS_MONTH_DAY = {
    1: {"start": (1, 1), "end": (31, 3)},
    2: {"start": (1, 4), "end": (30, 6)},
    3: {"start": (1, 7), "end": (30, 9)},
    4: {"start": (1, 10), "end": (31, 12)}
}

LR_MONTHS_QUARTERS = {
    1: 3, 2: 3, 3: 3, 4: 4, 5: 4, 6: 4, 7: 1, 8: 1, 9: 1, 10: 2, 
    11: 2, 12: 2
}

LR_QUARTERS_MONTH_DAY = {
    3: {"start": (1, 1), "end": (31, 3)},
    4: {"start": (1, 4), "end": (30, 6)},
    1: {"start": (1, 7), "end": (30, 9)},
    2: {"start": (1, 10), "end": (31, 12)}
}

LR_PERIODS_MONTH_DAY = {
    "M7": {"start": (1, 1), "end": (31, 1)},
    "M8": {"start": (1, 2), "end": (28, 2)},
    "M9": {"start": (1, 3), "end": (31, 3)},
    "M10": {"start": (1, 4), "end": (30, 4)},
    "M11": {"start": (1, 5), "end": (31, 5)},
    "M12": {"start": (1, 6), "end": (30, 6)},
    "M13": {"start": (1, 6), "end": (30, 6)},
    "M0": {"start": (1, 7), "end": (31, 7)},
    "M1": {"start": (1, 7), "end": (31, 7)},
    "M2": {"start": (1, 8), "end": (31, 8)},
    "M3": {"start": (1, 9), "end": (30, 9)},
    "M4": {"start": (1, 10), "end": (31, 10)},
    "M5": {"start": (1, 11), "end": (30, 11)},
    "M6": {"start": (1, 12), "end": (31, 12)}
}

LR_QUARTERS_CAL_QUARTERS = {
    1: 3,
    2: 4,
    3: 1,
    4: 2
}

def lr_quarter_to_cal_quarter(_fy, _fq):
    if _fq in (3,4):
        year = _fy+1
    else:
        year = _fy
    quarter = LR_QUARTERS_CAL_QUARTERS[_fq]
    return year, quarter

def fp_fy_to_date(fp, fy, start_end='start'):
    """Convert from LR FP, FY to real date."""
    if fp in ("M7","M8","M9","M10","M11","M12","M13"):
        year = fy+1
    else:
        year = fy
    day, month = LR_PERIODS_MONTH_DAY[fp][start_end]
    return datetime.datetime(year, month, day)

def fq_fy_to_date(fq, fy, start_end='start'):
    """Convert from LR FQ, FY to real date."""
    if fq in (3,4):
        year = fy+1
    else:
        year = fy
    day, month = LR_QUARTERS_MONTH_DAY[fq][start_end]
    return datetime.datetime(year, month, day)

def date_to_fy_fq(date):
    quarter = LR_MONTHS_QUARTERS[date.month]
    # Q3 and Q4 (Jan-Jun) are FY of previous year
    if quarter in (3, 4):
        year = date.year-1
    else:
        year = date.year
    return year, quarter

def isostring_date(value):
    # Returns a date object from a string of format YYYY-MM-DD
    if value == "": return None
    return datetime.datetime.strptime(value[0:10], "%Y-%m-%d")

def isostring_year(value):
    # Returns a date object from a string of format YYYY
    return datetime.datetime.strptime(value, "%Y")

def subtract_one_quarter(from_year, from_quarter):
    if from_quarter > 1:
        return from_year, from_quarter-1
    else:
        return from_year-1, 4

def add_one_quarter(from_year, from_quarter):
    if from_quarter < 4:
        return from_year, from_quarter+1
    else:
        return from_year+1, 1

def available_fy_fqs():
    return ["{} Q{} (D)".format(year, quarter) for year in ALLOWED_YEARS for quarter in (1,2,3,4)]

def current_fy_fq():
    year, quarter = date_to_fy_fq(datetime.datetime.utcnow())
    return "{} Q{} (D)".format(year, quarter)

def previous_fy_fq():
    year, quarter = date_to_fy_fq(datetime.datetime.utcnow())
    year, quarter = subtract_one_quarter(year, quarter)
    return "{} Q{} (D)".format(year, quarter)

def previous_fy_fq_numeric():
    year, quarter = date_to_fy_fq(datetime.datetime.utcnow())
    return subtract_one_quarter(year, quarter)

def available_fy_fqs_as_dict():
    return [{'value': fyfqstring,
             'text': column_data_to_string(fyfqstring),
             'selected': {True: ' selected', 
                          False: ''}[previous_fy_fq() == fyfqstring]
              } for fyfqstring in available_fy_fqs()]

def get_data_from_header(column_name):
    pattern = "(\d*) Q(\d) \(D\)"
    result = re.match(pattern, column_name).groups()
    return (result[1], result[0])

def fy_to_fyfy(fy):
    """Converts a fiscal year to a year + year+1 e.g. 2018 to 1819"""
    return "{}{}".format(fy[2:4], str(int(fy)+1)[2:4])

def column_data_to_string(column_name):
    fq, fy = get_data_from_header(column_name)
    fyfy = fy_to_fyfy(fy)
    return u"FY{} Q{} Disbursements".format(fyfy, fq)

def make_quarters_text(list):
    return [{"quarter_name": "Q{}".format(k),
        "quarter_months": "{}-{}".format(
        datetime.date(2019, l["start"][1], l["start"][0]).strftime("%b"),
        datetime.date(2019, l["end"][1], l["end"][0]).strftime("%b")
    )} for k, l in list.items()]
