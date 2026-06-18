<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_compat04.py -->
# sources/storage-engines/wiredtiger/test/suite/test_compat04.py

Purpose: verifies that a database created at one compatibility release can be reconfigured to another release and then reopened with that release as both current and required maximum.

Important APIs and control flow: `conn_config()` creates the initial database with `config_base=true/false`, logging, and optional `compatibility=(release=...)`. `test_compat04()` creates a logged table, inserts 2000 integer records to force multiple log files, calls `self.conn.reconfigure('compatibility=(release=...)')`, closes the connection, and reopens with `compatibility=(release=...,require_max=...)`.

State, persistence, and dependencies: the persistent state is a logged WiredTiger home with table metadata and log files generated under different compatibility settings. Dependencies are `wttest`, `suite_subprocess`, `make_scenarios`, the WiredTiger connection reconfiguration path, and log compatibility code.

Integration points: exercises the upgrade/downgrade compatibility lane after initial creation, including `config_base` variants and patch-number parsing such as `3.0.0`.

Risks and test signals: the test assumes every listed release transition is legal; release table changes can invalidate expectations. Success is a clean reopen after reconfiguration with no data verification beyond successful log/database recovery, so failures usually identify compatibility metadata or log-version negotiation regressions.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_compat04.py -->
