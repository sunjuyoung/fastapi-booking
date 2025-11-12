from appserver.libs.datetime.calendar import get_start_weekday_of_month, get_last_day_of_month, get_range_days_of_month
import pytest

def test_get_start_weekday_of_month():
  assert get_start_weekday_of_month(2024, 12) == 6
  
  
  
def test_get_last_day_of_month():
  assert get_last_day_of_month(2024, 12) == 31


@pytest.mark.parametrize("year, month, expected", [
  (2024, 12, 31),
  (2025, 1, 31),
  (2025, 2, 28),
  (2025, 3, 31),
  (2025, 4, 30),
  (2025, 5, 31),
  (2025, 6, 30),
  (2025, 7, 31),
  (2025, 8, 31),
  (2025, 9, 30),
  (2025, 10, 31),
  (2025, 11, 30),
  (2025, 12, 31),
])
def test_get_last_day_of_month(year, month, expected):
  assert get_last_day_of_month(year, month) == expected
  






@pytest.mark.parametrize("year, month, expcted_padding_count, expected_total_count", [
  (2024, 12, 0, 31),
  (2024,3,5,36)

])
def test_get_range_days_of_month(year, month, expcted_padding_count, expected_total_count):
  days = get_range_days_of_month(year, month)
  padding_count = days[:expcted_padding_count]
  
  assert sum(padding_count) == 0
  assert days[expcted_padding_count] == 1
  assert len(days) == expected_total_count
