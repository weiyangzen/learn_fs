# sources/storage-engines/wiredtiger/test/suite/test_compat01.py

Purpose: tests compatibility release configuration effects on log versions, log removal, reconfiguration, restart, and active-transaction restrictions.

Important APIs and types: `WiredTigerTestCase`, `suite_subprocess.runWt(["printlog"])`, `conn.reconfigure`, `wiredtiger_open`, `SimpleDataSet`, `make_scenarios`, and filesystem log enumeration.

Control flow: scenario matrix creates a database with an initial compatibility release, writes enough records to generate logs, then either reconfigures compatibility in-place or restarts with a new release. `check_prev_lsn` runs `wt printlog` and searches for `prev_lsn` records to infer log version. It also checks whether old log files remain or are removed on downgrade. `test_reconfig_fail` verifies compatibility upgrade/downgrade is blocked by an active transaction while unrelated reconfigure is allowed.

State and persistence behavior: compatibility release controls log format version and whether newer logs can remain when downgrading. Restart path forces recovery and log cleanup.

Dependencies and integration points: command-line `wt printlog`, connection compatibility parser, logging subsystem, file retention, and scenario pruning.

Risks: large compatibility matrix is pruned but still broad. Log file naming and `printlog` output strings are part of the test contract.

Test signals: `prev_lsn` presence matches expected log version, log removal behavior matches downgrade rules, and active transaction blocks compatibility reconfigure with a quiescence error.
