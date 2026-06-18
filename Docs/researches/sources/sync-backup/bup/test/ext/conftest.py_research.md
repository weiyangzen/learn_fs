## sources/sync-backup/bup/test/ext/conftest.py

Purpose: pytest collector for Bup’s executable `test-*` shell scripts using the wvtest protocol.

Important APIs and control flow: `BupSubprocTestRunner.runtest()` creates a temporary HOME under `test/tmp`, runs the script as a subprocess, writes combined output to pytest stdout, maps `! ... skip ok` lines to `pytest.skip`, detects `! ... failed` lines and `AssertionError`, and raises `BupSubprocFailure` with status/failure lines. `BupSubprocTestFile.collect()` yields one runner per executable file. `pytest_collect_file()` supports pytest 6 and 7 APIs. `_collect_item()` ignores backup files and marks `test-versioning-and-archive` as release.

State and dependencies: per-test temporary HOME is the main state isolation mechanism. It depends on `pytest`, `bup.helpers.temp_dir`, and byte-stream output handling.

Risks and tests: all shell output is buffered before inspection, so very large output can be memory-heavy. Failure detection depends on wvtest line conventions. This file is the test harness for every listed `test/ext/test-*` script.
