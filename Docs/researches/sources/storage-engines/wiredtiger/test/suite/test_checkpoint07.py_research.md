# sources/storage-engines/wiredtiger/test/suite/test_checkpoint07.py

Purpose: tests dsrc statistic `btree_clean_checkpoint_timer` behavior for clean vs dirty tables, forced checkpoints, and backup cursor pinning.

Important APIs/types/functions: `stat.dsrc.btree_clean_checkpoint_timer`, checkpoint `force=true`, backup cursor `backup:`, precise/fuzzy scenarios, and tiered skip.

Control flow: create three tables, insert initial rows and checkpoint, dirty table 1 and checkpoint, assert table 1 timer is zero while clean tables have nonzero timers. Force checkpoint and assert all timers reset to zero. Dirty tables 1 and 2 and checkpoint, expecting only table 3 to have a clean timer. Open a backup cursor, perform writes/checkpoints so pinned checkpoints affect timer values, compare finite timer values against the saved "forever" value, close backup cursor, and confirm clean table timer returns to forever behavior.

State/persistence behavior: the timer records whether clean checkpoints can be skipped or must be retained because backup pins older checkpoint generations.

Dependencies/integration: checkpoint cleaner, backup cursor, per-dsrc statistics, precise timestamp setup.

Risks/test signals: time values can differ by one second, handled by tolerance checks. Failures indicate clean checkpoint timer accounting regressions.
