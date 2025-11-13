import pytest
from pydantic import ValidationError
from sqlalchemy.ext.asyncio import AsyncSession
from appserver.apps.account.endpoints import signup
from appserver.apps.account.models import User
from fastapi.testclient import TestClient
from appserver.apps.account.exceptions import DuplicatedUsernameError, DuplicatedEmailError

async def test_모든_입력_항목을_유효한_값으로_입력하면_계정이_생성된다(
    client: TestClient,
    db_session: AsyncSession
):
    payload = {
        "username": "test",
        "email": "test@example.com",
        "display_name": "test",
        "password": "test테스트1234",
    }

    result = await signup(payload, db_session)

    assert isinstance(result, User)
    assert result.username == payload["username"]
    assert result.email == payload["email"]
    assert result.display_name == payload["display_name"]
    assert result.is_host is False

    response = client.get(f"/api/accounts/users/{payload['username']}")
    assert response.status_code == 200
    data = response.json()
    assert data["username"] == payload["username"]
    assert data["email"] == payload["email"]
    assert data["display_name"] == payload["display_name"]
    assert data["is_host"] is False
    
    
    
@pytest.mark.parametrize("username",[
    "oweifjewoifjeijfiewfewjfefijioewfoewjfoiewjfiewoiwefiejwfoiewjfoiewjfoiwejfoiwejf",
    "we",
    "x",
])
async def test_username_길이_검증(client: TestClient, db_session: AsyncSession, username: str):
    payload = {
        "username": username,
        "email": "test@example.com",
        "display_name": "test",
        "password": "test테스트1234",
    }
    
    with pytest.raises(ValidationError) as excinfo:
        await signup(payload, db_session)
        
async def test_id_중복_검증(client: TestClient, db_session: AsyncSession):
    payload = {
        "username": "test",
        "email": "test@example.com",
        "display_name": "test",
        "password": "test테스트1234",
    }
    
    await signup(payload, db_session)
    
    payload["email"] = "test2@example.com"
    with pytest.raises(DuplicatedUsernameError) as exc:
        await signup(payload, db_session)




async def test_email_중복_검증(client: TestClient, db_session: AsyncSession):
    payload = {
        "username": "test",
        "email": "test@example.com",
        "display_name": "test",
        "password": "test테스트1234",
    }
    
    await signup(payload, db_session)
    
    payload["username"] = "test2"
    with pytest.raises(DuplicatedEmailError) as exc:
        await signup(payload, db_session)



async def test_표시명을_입력하지_않으면_무작위_문자열_8글자로_대신한다(db_session: AsyncSession):
    payload = {
        "username": "test",
        "email": "test@example.com",
        "password": "test테스트1234",
    }

    user = await signup(payload, db_session)
    assert isinstance(user.display_name, str)
    assert len(user.display_name) == 8


