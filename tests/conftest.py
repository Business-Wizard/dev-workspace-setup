from _pytest.main import Session


def pytest_sessionfinish(session: Session, exitstatus: int):
    if exitstatus == 5:
        session.exitstatus = 0
