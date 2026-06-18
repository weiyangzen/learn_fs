# sources/user-network-fs/pyfuse3/test/conftest.py

Purpose: Pytest configuration for pyfuse3 tests, including suspicious-output checks, source-tree import setup, logging control, warning policy, and teardown garbage collection.

Important APIs/types/functions: Registers `pytest_checklogs` plugin. Autouse fixture `register_false_checklog_pos` suppresses known deprecation and valgrind messages. `pytest_addoption` adds `--installed` and `--logdebug`. `pytest_pyfunc_call` delays after failures. `pytest_configure` updates `sys.path`/`PYTHONPATH`, enables faulthandler, configures warnings and logging. `pytest_runtest_teardown` forces `gc.collect`.

Control flow: Pytest loads this before tests. Unless `--installed` is set, source `src` is preferred for imports and subprocesses inherit the same `PYTHONPATH`. Logging defaults disable debug unless requested.

State and persistence: Mutates process environment, `sys.path`, Python warnings filters, logging levels, and per-test false-positive registries.

Dependencies and integration points: Integrates with `pytest_checklogs.py`, pyfuse3 subprocess examples, and tests that rely on clean stderr/stdout.

Risks: The source import branch checks for `setup.py`, which may be stale in a pyproject-first project; if absent, source insertion may not occur. Strict output checking can fail tests for benign new warnings unless registered.

Test signals: This file is itself test infrastructure; failures in warning/log output are surfaced by the plugin after every test.
