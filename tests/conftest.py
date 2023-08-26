def pytest_sessionstart(session):
    # do not raise on error code 5, when pytest collects no tests
    if session.exitstatus == 5:
        session.exitstatus = 0
