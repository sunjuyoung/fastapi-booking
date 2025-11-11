from datetime import datetime, timezone, time, date
from sqlmodel import SQLModel, Field, Relationship, Text, JSON, func
from sqlmodel.main import SQLModelConfig
from pydantic import EmailStr, AwareDatetime
from sqlalchemy import UniqueConstraint
from sqlalchemy_utc import UtcDateTime
from sqlalchemy.dialects.postgresql import JSONB
from typing import TYPE_CHECKING, Union

# - `id`
# - `user_id` : 회원 id
# - `topics` : Array 캘린더 주제
# - `description` : 캘린더 설명
# - `google_calendar_id` : 구글 캘린더 id

if TYPE_CHECKING:
  from appserver.apps.account.models import User


class Calendar(SQLModel, table=True):
  __tablename__ = "calendars"

  id: int = Field(default=None, primary_key=True)
  
  host_id: int = Field(foreign_key="users.id", unique=True)
  
  #1:1관계는 어느 쪽에서 관계를 짓던 상관없습니다.
  host: "User" = Relationship(back_populates="calendar", sa_relationship_kwargs={"uselist": False, "single_parent": True})
  
  #리스트형 객체 , 이를 데이터베이스에서 JSON자료형으로 다룹니다.
  # postgresql에서 JSONB자료형으로 다룹니다.
  #개발단계에ㅓ는 SQLite3 사용 하므로 , postgresql사용시에만 JSONB자료형으로 다룹니다. 그 외는 JSON
  topics: list[str] = Field(
    sa_type=JSON().with_variant(JSONB(astext_type=Text()), "postgresql"),
    description="캘린더 주제")
  
  description: str = Field(sa_type=Text, description="캘린더 설명")
  google_calendar_id: str = Field(max_length=1024, description="구글 캘린더 id")

  time_slots: list["TimeSlot"] = Relationship(back_populates="calendar")

  created_at: AwareDatetime = Field(
    default=None,
    nullable=False,
    sa_type=UtcDateTime,
    sa_column_kwargs={"server_default": func.now()})
  
  updated_at: AwareDatetime = Field(
    default=None,
    nullable=False,
    sa_type=UtcDateTime,
    sa_column_kwargs={"server_default": func.now(), "onupdate": lambda : datetime.now(timezone.utc) })
  
  
  
class TimeSlot(SQLModel, table=True):
    __tablename__ = "time_slots"

    id: int = Field(default=None, primary_key=True)
    start_time: time
    end_time: time
    #파이썬에서 요일은 정수로 다르며 월요일은 0, 일요일은 6입니다.
    weekdays: list[int] = Field(
        sa_type=JSON().with_variant(JSONB(astext_type=Text()), "postgresql"),
        description="예약 가능한 요일들"
    )

    calendar_id: int = Field(foreign_key="calendars.id")
    calendar: Calendar = Relationship(
        back_populates="time_slots",
    )

    bookings: list["Booking"] = Relationship(
    back_populates="time_slot",
    )


    created_at: AwareDatetime = Field(
        default=None,
        nullable=False,
        sa_type=UtcDateTime,
        sa_column_kwargs={
            "server_default": func.now(),
        },
    )
    updated_at: AwareDatetime = Field(
        default=None,
        nullable=False,
        sa_type=UtcDateTime,
        sa_column_kwargs={
            "server_default": func.now(),
            "onupdate": lambda: datetime.now(timezone.utc),
        },
    )
    

class Booking(SQLModel, table=True):
    __tablename__ = "bookings"

    id: int = Field(default=None, primary_key=True)
    when: date
    topic: str
    description: str = Field(sa_type=Text, description="예약 설명")
    
    time_slot_id: int = Field(foreign_key="time_slots.id")
    time_slot: TimeSlot = Relationship(
        back_populates="bookings",
    )
    
    guest_id: int = Field(foreign_key="users.id")
    guest: "User" = Relationship(
        back_populates="bookings",
    )
    
    created_at: AwareDatetime = Field(
        default=None,
        nullable=False,
        sa_type=UtcDateTime,
        sa_column_kwargs={"server_default": func.now()})
    updated_at: AwareDatetime = Field(
        default=None,
        nullable=False,
        sa_type=UtcDateTime,
        sa_column_kwargs={"server_default": func.now(), "onupdate": lambda : datetime.now(timezone.utc)})