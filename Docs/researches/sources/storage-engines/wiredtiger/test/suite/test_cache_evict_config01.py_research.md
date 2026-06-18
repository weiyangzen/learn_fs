# sources/storage-engines/wiredtiger/test/suite/test_cache_evict_config01.py

Purpose: validates dynamic reconfiguration of cache eviction controls and rejects invalid eviction ranges without restarting the connection.

Important APIs/types/functions: `conn.reconfigure`, `wiredtiger.WiredTigerError`, `assertRaisesException`, and table cursor read/write operations. Connection config enables `cache_size=50MB,statistics=(all)`.

Control flow: create a table and insert baseline rows; iterate through valid `eviction=[...]` configurations covering `incremental_app_eviction`, `prefer_scrub_eviction`, `app_eviction_min_cache_fill_ratio`, `skip_update_obsolete_check`, and `cache_tolerance_for_app_eviction`; after each reconfigure write/read rows to prove the connection is alive. Then assert invalid negative or too-large ratio/tolerance configs raise `Invalid argument`.

State/persistence behavior: data updates are only liveness checks; the key state is mutable connection-level eviction configuration.

Dependencies/integration: configuration parser, live connection reconfigure path, eviction option validation, and stderr filtering for expected invalid-argument output.

Risks/test signals: does not verify runtime eviction behavior, only acceptance/rejection and continued usability.
