def pytest_sessionfinish(session, exitstatus):  # pyright: ignore[reportMissingParameterType, reportUnknownParameterType]
    if exitstatus == 5:
        session.exitstatus = 0
