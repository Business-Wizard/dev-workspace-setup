def pytest_sessionfinish(session, exitstatus: int):  # noqa: ANN001  # type: ignore UnknownParameterType
    if exitstatus == 5:
        session.exitstatus = 0
