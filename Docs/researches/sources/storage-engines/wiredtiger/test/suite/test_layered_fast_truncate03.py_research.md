<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate03.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate03.py

Purpose: proves follower reads of leader fast-truncated pages do not dirty stable pages and that deleted state survives eviction, follower reopen, ingest writes, and timestamped instantiation.

Important APIs/types/functions: `test_layered_fast_truncate03` uses `wiredtiger.stat`, `cache_pages_dirty`, `cache_read_deleted`, mixin helpers `evict_range`, `search_at`, `open_follower`, and a local `advance_follower` wrapper around leader checkpoint plus `disagg_advance_checkpoint`.

Control flow: `setup_leader` inserts timestamped rows, checkpoints, and evicts all pages; optional `leaf_page_max=4096` forces many leaf pages. `test_no_dirty_on_read` reads sample deleted keys, evicts/reloads them, and asserts dirty-page stats stay unchanged. `test_page_split_with_ingest_writes` writes a subset of truncated keys on the follower after checkpoint advance and checks timestamped visibility. `test_state_preserved_on_reopen` opens two cold follower connections against the same checkpoint. `test_instantiation_not_globally_visible` reads below the truncate timestamp, expecting `cache_read_deleted` to rise without dirtying.

State and persistence behavior: deleted-page state is kept as checkpoint metadata / fast-delete state, while later ingest writes override only their keys at later timestamps.

Dependencies/integration points: depends on statistics stability, debug eviction, disaggregated checkpoint pickup, and timestamp reads. Risks are false negatives if page eviction does not happen or stats are reused unexpectedly. Test signals are WT_NOTFOUND, stable values, and counter deltas.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate03.py -->
