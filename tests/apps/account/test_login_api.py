from fastapi import status
from fastapi.testclient import TestClient


from appserver.apps.account.schemas import LoginPayload, SignupPayload
from appserver.apps.account.models import User
from appserver.apps.account.utils import ACCESS_TOKEN_EXPIRE_MINUTES


async def test_로그인_성공(host_user: User, client: TestClient):
    payload = LoginPayload.model_validate({
        "username": host_user.username,
        "password": "testtest",
    })
    
    response = client.post("/api/accounts/login", json=payload.model_dump())

    assert response.status_code == status.HTTP_200_OK
    data = response.json()

    

    data = response.json()
    assert data["access_token"] is not None
    assert data["token_type"] == "bearer"
    assert data["user"]["username"] == host_user.username
    assert data["user"]["display_name"] == host_user.display_name
    assert data["user"]["is_host"] == host_user.is_host

    cookie = response.cookies.get("auth_token")
    assert cookie is not None
    assert cookie == data["access_token"]