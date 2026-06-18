# sources/storage-engines/wiredtiger/test/3rdparty/testtools-2.7.1/testtools/runtest.py

Purpose: core object that executes a single `testtools.TestCase` and reports to extended or legacy result APIs.

Important APIs, types, and functions: `MultipleExceptions` aggregates cleanup/setup exceptions. `RunTest` owns `case`, `handlers`, `result`, `_exceptions`, and `last_resort`. Key methods are `run()`, `_run_one()`, `_run_prepared_result()`, `_run_core()`, `_run_cleanups()`, `_run_user()`, and `_got_user_exception()`. `_raise_force_fail_error()` supports delayed expectation failures.

Control flow: `run()` creates a default result if needed and starts/stops the run. `_run_prepared_result()` starts the test, runs setup/test/teardown/cleanups, then reports one captured exception through the first matching handler. `_run_core()` skips before setup when decorators mark skip, always runs cleanups after setup failure, and reports success only when no failure and no forced failure occurred.

State and persistence: per-run state is `_exceptions`, result, and case detail mutations. No persistence.

Dependencies and integration points: depends on `ExtendedToOriginalDecorator` so code can use extended result APIs against old results. Used by `TestCase.run()` and custom run-test factories.

Risks and test signals: all exceptions are initially caught, including system-exiting exceptions, so cleanup can run before re-raise/report. Only one exception is reported from `_exceptions.pop()` after the run, though `MultipleExceptions` can expand multiple captured errors. Test signals cover setup failure, cleanup ordering, skip handling, forced failure, and legacy result adaptation.
