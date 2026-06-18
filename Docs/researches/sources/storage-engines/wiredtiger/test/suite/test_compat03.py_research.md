<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_compat03.py -->
# sources/storage-engines/wiredtiger/test/suite/test_compat03.py

Purpose: exercises WiredTiger compatibility parsing at database creation time, especially `compatibility=(release=...)`, `require_max`, and `require_min` against expected log-version ranges.

Important APIs and control flow: `test_compat03` inherits `WiredTigerTestCase` and `suite_subprocess`, builds a Cartesian scenario matrix with `make_scenarios`, creates a separate `TEST` home, assembles `wiredtiger_open` configuration strings with logging enabled, and decides whether the open should fail based on future releases, max/min ordering, and release/log compatibility. Successful scenarios open and close the connection; failing scenarios assert `WiredTigerError` with a version-incompatibility pattern.

State, persistence, and dependencies: the test creates a WiredTiger home and log-enabled database metadata but does not populate tables. It depends on `wiredtiger`, `wttest`, `suite_subprocess`, `wtscenario`, filesystem directory creation, and compatibility/log version mappings embedded in the test.

Integration points: covers the public `wiredtiger_open` compatibility API, log version selection, patch-version normalization, and startup validation before normal workload execution.

Risks and test signals: scenario expectations are tightly coupled to the release-to-log-version table; when adding releases, `future_logv`, default log version, and max/min lists must be updated together. Test pass/fail signals are correct rejection of impossible/future requirements and acceptance of legal compatibility combinations.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_compat03.py -->
