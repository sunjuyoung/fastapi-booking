from datetime import date, timedelta


def get_start_weekday_of_month(year: int, month: int):
  result = date(year, month, 1)
  return result.weekday()



def get_last_day_of_month(year: int, month: int):
  if month == 12:
    next_month = date(year + 1, 1, 1)
  else:
    next_month = date(year, month + 1, 1)
    
  result = next_month - timedelta(days=1)
  return result.day



def get_range_days_of_month(year: int, month: int):
  #월의 시작 요일을 가져옴 (월 0 , 일 6)
  start_weekday = get_start_weekday_of_month(year, month)
  #월의 마지막 날을 가져옴
  last_day = get_last_day_of_month(year, month)
  
  #월요일을 1로 변경
  start_weekday = (start_weekday + 1) % 7
  
  result = [0] * start_weekday # 시작 요일 전까지 0으로 채움
  
  for day in range(1, last_day + 1):
    result.append(day)
    
  return result
  
# import calendar

# cal = calendar.Calendar(calendar.SUNDAY)
# print(list(cal.itermonthdays(2025,11)))