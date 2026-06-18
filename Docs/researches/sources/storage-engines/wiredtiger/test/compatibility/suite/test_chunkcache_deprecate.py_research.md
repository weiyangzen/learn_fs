# sources/storage-engines/wiredtiger/test/compatibility/suite/test_chunkcache_deprecate.py

Purpose: Validates upgrade behavior when a database with chunk-cache configuration is opened on a branch where chunk cache is deprecated.

Important APIs/types/functions: `test_chunkcache_deprecate` gates execution by `WTVersion` boundaries. `on_older_branch` creates a database with `chunk_cache=(enabled=false,capacity=1GB)`, writes 100 rows, and closes it. `on_newer_branch_disabled` verifies open succeeds with a warning and data remains readable. `_set_basecfg_chunkcache_enabled` flips `WiredTiger.basecfg` between enabled/disabled. `on_newer_branch_enabled` and `chunk_cache_enabled_unsupported` expect clean `ENOTSUP`.

Control flow: older branches before chunk-cache introduction skip; deprecated branches directly test unsupported enabled config; crossing the deprecation boundary runs create, open-with-warning, mutate basecfg, then open-fails.

State and persistence: persists chunk-cache settings in `WiredTiger.basecfg` and table rows in the shared test home across branch-specific subprocesses.

Dependencies/integration: uses `CompatibilityTestCase.run_method_on_branch`, `WTVersion`, Python `wiredtiger`, `errno`, and captured-output checks.

Risks and test signals: exact warning/error text is part of the test signal, so message churn can fail tests. Manual basecfg replacement assumes a simple `enabled=` token. Data verification prevents false positives where open succeeds but upgraded contents are unusable.
