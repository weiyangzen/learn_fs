# sources/user-network-fs/sshfs/test/conftest.py

Purpose: pytest configuration that improves failure diagnostics and fails tests on suspicious process output.

Important APIs/types/functions: `pytest_pyfunc_call` sleeps after a failed test; `pass_capfd` fixture attaches capture to unittest instances; `check_test_output` replays captured output, strips registered false positives, and scans for suspicious words/Valgrind prefixes; `register_output` monkeypatch helper; autouse `save_cap_fixtures`; `pytest_runtest_call` invokes output checks.

Control flow: every test gets a `capfd.false_positives` list and monkeypatched registration method. After test call, output is checked unless capture is disabled. Suspicious stdout/stderr raises `AssertionError`.

State and persistence behavior: uses module-global `current_capfd`, intentionally relying on sequential pytest execution.

Dependencies and integration points: pytest hook system, `capfd`, regex scanning, and test modules that can register expected output.

Risks: the global fixture hack is incompatible with parallel pytest execution. Broad suspicious-word scanning may create false positives. Output checks occur after the test body and can mask original intent if not diagnosed carefully.

Test signals: pytest self-behavior through the suite, false-positive registration tests if present, and no suspicious output in sshfs runtime tests.
