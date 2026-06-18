# sources/user-network-fs/pyfuse3/test/pytest_checklogs.py

Purpose: Pytest plugin that fails tests on suspicious stdout/stderr text or warning-and-above log records unless explicitly registered as expected.

Important APIs/types/functions: `CountMessagesHandler`, context manager `assert_logs`, `check_test_output`, `register_output`, fixture `reg_output`, and autouse fixture `check_output`.

Control flow: `check_output` yields to the test, scans captured log records from setup/call/teardown for warning-or-higher unignored records, then scans stdout/stderr for words such as exception, error, warning, fatal, traceback, fault, crash, abort, and fishy. `assert_logs` temporarily attaches a handler that marks matching records as ignored and optionally asserts exact count.

State and persistence: Per-test state is stored on `request.node.checklogs_fp`. Log records may get `checklogs_ignore=True`. No persistent state.

Dependencies and integration points: Used by `conftest.py` as a plugin. Integrates with pytest `capfd`/`caplog` and test code that expects warnings.

Risks: Regex-based suspicious output matching can produce false positives on legitimate output. `assert_logs` matches `record.msg` before formatting, so formatted output text may not match.

Test signals: Every test using this conftest gets output/log checking automatically.
