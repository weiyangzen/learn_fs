<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_compat05.py -->
# sources/storage-engines/wiredtiger/test/suite/test_compat05.py

Purpose: checks backward-compatible log archive configuration aliases, verifying how `archive` and `remove` settings control log file deletion.

Important APIs and control flow: scenarios vary `log=(...,archive=...,remove=...)`. `conn_config()` enables logging with small `file_max`; `test_compat05()` populates 10000 rows through `SimpleDataSet`, asserts that a second log exists, checkpoints, then `check_remove()` polls up to 90 seconds for `WiredTigerLog.0000000001` to disappear.

State, persistence, and dependencies: the test persists log files in the WiredTiger home and relies on the background log removal/archive machinery after checkpoint. It depends on `SimpleDataSet`, `wttest`, `suite_subprocess`, filesystem `os.path.exists`, and time-based polling. It is skipped for tiered storage.

Integration points: targets compatibility of old `archive` spelling versus current `remove` semantics, including override ordering when both appear.

Risks and test signals: the one-second polling loop can be slow or timing-sensitive on loaded machines. A pass means the first log is retained or deleted exactly as the scenario declares; failures indicate config parsing precedence or log archive scheduling regressions.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_compat05.py -->
