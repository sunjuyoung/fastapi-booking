import string
import random
from datetime import datetime, timezone
from sqlmodel import SQLModel, Field, func, Relationship
from pydantic import EmailStr, AwareDatetime, model_validator
from sqlalchemy import UniqueConstraint
from sqlalchemy_utc import UtcDateTime
from typing import TYPE_CHECKING
from appserver.apps.calendar.models import Calendar, Booking

#파이썬이 자료형 검사를 할때만 실행, 실제 동작할때 runtime에는 실행되지 않습니다.
if TYPE_CHECKING:
    from appserver.apps.calendar.models import Calendar, Booking

class User(SQLModel, table=True):
  __tablename__= "users"
  __table_args__ =(
    UniqueConstraint("email", name="uq_email"),
  )
  
  id: int = Field(default=None, primary_key=True)
  username: str = Field(min_length=4, max_length=40, description="사용자 계정 ID")
  email: EmailStr = Field(unique=True, max_length=128, description="사용자 이메일")
  display_name: str = Field(min_length=4, max_length=40, description="사용자 표시 이름")
  is_host: bool = Field(default=False, description="사용자가 호스트인지 여부")
  hashed_password: str = Field(min_length=4, max_length=128, description="사용자 비밀번호")
  
  #OAuthAccount 문자열로 표기하면 해당 자료형을 지연 로딩, 파이썬에서는 문자열 각주 또는 전방 참조라고 합니다.
  oauth_accounts: list["OAuthAccount"] = Relationship(back_populates="user")
  
  #single_parent 한 부모 객체에게만 연결되면 부모 객체가 삭제될때 자식 객체도 삭제됩니다.
  #uselist 연결된 객체가 여러개인지 여부 
  calendar: "Calendar" = Relationship(back_populates="host", sa_relationship_kwargs={"uselist": False, "single_parent": True})
  
  
  bookings: list["Booking"] = Relationship(
    back_populates="guest",
    )
  
  #server_default 데이터베이스 영역에서 기본값을 설정하는 옵션
  #onupdate ORM에 객체데이터가 업데이트 시 파이썬 객체를 받아서 사용할 수 있도록 하는 옵션(ORM영역)
  created_at: AwareDatetime = Field(
    default=None, 
    nullable=False,
    sa_type=UtcDateTime,
    sa_column_kwargs={"server_default": func.now()})
  
  updated_at: AwareDatetime = Field(
    default=None,
    nullable=False,
    sa_type=UtcDateTime,
    sa_column_kwargs={"server_default": func.now(), 
                      "onupdate": lambda : datetime.now(timezone.utc) }
  )
  
  # @model_validator(mode="before")
  # @classmethod
  # def validate_display_name(cls, data: dict):
  #   if not data.get("display_name"):
  #     data["display_name"] = "".join(random.choices(string.ascii_letters + string.digits, k=8))
  #   return data
  
  
  
  
  


class OAuthAccount(SQLModel, table=True):#
  __tablename__ = "oauth_accounts"
  __table_args__ = (
    UniqueConstraint("provider", "provider_account_id", name="uq_provider_account_id"),
  )
  
  id: int = Field(default=None, primary_key=True)
  
  #foreign_key 외래키 제약조건 설정 , 테이블이름과 기본키이름을 합친 문자열
  user_id: int = Field(foreign_key="users.id", nullable=False)
  #Relationship() relationshipInfo객체를 반환하는 함수입니다
  user: User = Relationship(back_populates="oauth_accounts")
  
  provider: str = Field(nullable=False, max_length=10, description="OAuth 제공자")
  provider_account_id: str = Field(nullable=False, max_length=128, description="OAuth 제공자 계정 ID")
  
  
  
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