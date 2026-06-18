# sources/storage-engines/wiredtiger/test/suite/test_cache_evict_config02.py

Purpose: verifies that enabling `prefer_scrub_eviction` dynamically increases scrub/write-restore activity under cache pressure.

Important APIs/types/functions: `stat.conn.cache_write_restore_scrub`, `conn.reconfigure`, `statistics:` cursor, and repeated cursor updates. Connection config uses a small 5MB cache with statistics enabled.

Control flow: create a table, repeatedly update 100 keys 50,000 times with 5KB values to create dirty/update pressure, read baseline scrub statistic, reconfigure `eviction=[prefer_scrub_eviction=true]`, repeat the update workload, read the statistic again, and assert it increased.

State/persistence behavior: repeatedly overwrites the same key set, generating cache pressure and restored-update scrub opportunities. The durable row contents are not inspected.

Dependencies/integration: cache eviction, scrub eviction preference, runtime reconfiguration, and connection statistics.

Risks/test signals: statistic sensitivity can be workload/platform dependent. Failure means the flag did not measurably affect scrub eviction or stats were not updated.
