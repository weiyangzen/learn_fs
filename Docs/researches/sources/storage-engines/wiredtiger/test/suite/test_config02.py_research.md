<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_config02.py -->
# sources/storage-engines/wiredtiger/test/suite/test_config02.py

Purpose: validates `wiredtiger_open` home-directory resolution using explicit home arguments, `WIREDTIGER_HOME`, relative/absolute paths, and filesystem error cases.

Important APIs and control flow: setup disables the default connection/session open. `common_test()` optionally sets `WIREDTIGER_HOME`, opens with `create`, populates a table, and clears the environment in a `finally` block. Individual tests verify current directory, relative and absolute homes, explicit home taking precedence over environment, environment-only homes, missing directories, and non-writable directories.

State, persistence, and dependencies: each success path persists a `test_config02.wt` file in the selected home directory. Dependencies are `os.putenv`, `os.unsetenv`, directory permissions, `wiredtiger_open`, and cursor/table APIs. The suite skips tiered hooks because environment home selection conflicts with tiered behavior.

Integration points: targets the C/Python connection API boundary and environmental configuration handling.

Risks and test signals: permissions and environment APIs vary by platform, with Windows-specific skips. Pass/fail signals are correct file placement, empty unused env directory, and expected filesystem errors for missing or unwritable homes.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_config02.py -->
