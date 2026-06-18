# sources/storage-engines/wiredtiger/test/suite/test_compat02.py

Purpose: tests compatibility `release`, `require_min`, and `require_max` configuration interactions, including future-version rejection and base config handling.

Important APIs and types: `WiredTigerTestCase`, `suite_subprocess`, `make_scenarios`, `wiredtiger_open`, `assertRaisesWithMessage`, and compatibility connection config fields.

Control flow: create a database at a scenario release level with logging enabled, write enough records to produce logs, close with checkpoint verbose enabled, build a restart config from `require_min`, `require_max`, and `release`, compute whether the combination should fail based on associated log-version numbers, and then assert either version incompatibility or successful reopen.

State and persistence behavior: existing database log version and configured compatibility constraints determine whether restart is allowed. The test protects compatibility gating before opening an incompatible home.

Dependencies and integration points: logging, compatibility version-to-log-version mapping, future version handling, config base true/false, and scenario pruning.

Risks: error cases are intentionally checked by generic version-incompatibility message because exact error ordering depends on library code. Future version constants must stay beyond current supported versions.

Test signals: restart raises `Version incompatibility detected` when computed invalid; otherwise `wiredtiger_open` succeeds and closes cleanly.
