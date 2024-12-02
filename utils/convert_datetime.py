from datetime import datetime


# 날짜 객체로 변환
def convert_datetime(date):
    format = '%Y%m%d%H%M%S'
    dt_datetime = datetime.strptime(date, format)
    
    return dt_datetime