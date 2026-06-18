<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_stat14.py -->
# sources/storage-engines/wiredtiger/test/suite/test_stat14.py

Purpose: verifies eviction threshold statistics report default and reconfigured values using percentage values multiplied by 100 for two decimal places of precision.

Important APIs/types/functions: `test_stat14` uses `wiredtiger.stat.conn.eviction_threshold_*`, `Connection.reconfigure`, `helper.WiredTigerCursor`, and `statistic_uri`. The unused `get_stat` helper can assert data-source stats but the active test reads connection stats.

Control flow: open a connection statistics cursor and assert defaults for cache full target/trigger, dirty target/trigger, and auto-derived updates target/trigger. Then reconfigure each eviction threshold individually (`eviction_target`, `eviction_trigger`, `eviction_dirty_target`, `eviction_dirty_trigger`, `eviction_updates_target`, `eviction_updates_trigger`) and assert the corresponding stat reflects the scaled value.

State and persistence behavior: this is live connection configuration state, not persisted data state. Auto-derived defaults validate internal config normalization.

Dependencies/integration points: covers configuration parsing, reconfiguration, stats precision/scaling, and helper cursor context management. Risks include default value changes; signals are exact scaled integer stats after each config.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_stat14.py -->
