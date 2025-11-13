import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlmodel import SQLModel
from sqlalchemy.ext.asyncio import AsyncSession
from appserver.db import use_session, create_engine, create_session
from appserver.app import include_routers


@pytest.fixture(autouse=True)
async def db_session():
    dsn = "sqlite+aiosqlite:///:memory:"
    engine = create_engine(dsn)
    async with engine.connect() as conn:
        await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)

        session_factory = create_session(conn)
        async with session_factory() as session:
            yield session

        await conn.run_sync(SQLModel.metadata.drop_all)

        await conn.rollback()

    await engine.dispose()


@pytest.fixture()
def fastapi_app(db_session: AsyncSession):
    app = FastAPI()
    include_routers(app)

    async def override_use_session():
        yield db_session


    app.dependency_overrides[use_session] = override_use_session
    return app

@pytest.fixture()
def client(fastapi_app: FastAPI):
    with TestClient(fastapi_app) as client:
        yield client
