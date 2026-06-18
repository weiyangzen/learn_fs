# sources/test-tools/fio/t/readonly.py

Purpose: compact fio option test for `--readonly`. It confirms read workloads are allowed while write and trim workloads fail when `--readonly` is provided either before or after job options, and that all three workloads run without `--readonly`.

Important APIs and types: `FioReadOnlyTest` extends `FioJobCmdTest` and constructs a null-engine, one-second, time-based command. `TEST_LIST` defines nine cases with `SUCCESS_DEFAULT` or `SUCCESS_NONZERO` expectations.

Control flow: `main()` parses fio path and run filters, creates an artifact directory, resolves fio, then calls `run_fio_tests()`. `setup()` inserts `--readonly` at the beginning when `readonly-pre` is present, appends it when `readonly-post` is present, and otherwise omits it.

State and persistence: the null ioengine means no storage is modified. Only fiotestlib artifacts are written.

Dependencies and integration points: depends on Python, fio, fiotestlib, and fiotestcommon success constants. It is included in `run-fio-tests.py` as executable test 1003.

Risks and test signals: the main risk is that the test checks exit status only and not specific error messages, so it detects regressions in allow/fail behavior but not diagnostics. Success is the expected pass/fail matrix across read, write, trim, and option position.
