import pytest


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    # Execute all other hooks to obtain the report object
    outcome = yield
    rep = outcome.get_result()

    # Add the 'it' description to the report
    it_marker = item.get_closest_marker('it')
    if it_marker:
        rep.nodeid = f"{it_marker.args[0]} - {item.location}"
