<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate02.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate02.py

Purpose: validates that a follower reading a checkpoint containing leader-created fast-truncated pages sees correct MVCC visibility and cursor behavior.

Important APIs/types/functions: class `test_layered_fast_truncate02` uses `LayeredFastTruncateConfigMixin` helpers `leader_checkpoint`, `truncate`, `open_follower`, and `search_at`, plus `wiredtiger.WT_NOTFOUND`. It sets `cache_size=50MB,statistics=(all),disaggregated=(role="leader")` and creates a `layered:` table with integer keys.

Control flow: `setup_leader` inserts 5000 rows at timestamp 10, checkpoints, then walks a `debug=(release_evict)` cursor so truncation can use page-level fast-delete markers. `test_visibility` truncates 1001-4000 at ts=20, checkpoints, opens a follower, and checks deleted, boundary, and exterior keys at ts=20 and ts=15. `test_pre_truncation_read_sees_all_rows` scans at ts=10 and expects all rows. `test_cursor_scanning` verifies forward scans, reverse scans, and `search_near` skip the truncated range.

State and persistence behavior: the important state is a stable checkpoint containing fast-delete metadata and timestamped deletes that remain invisible to pre-truncate reads.

Dependencies/integration points: integrates eviction, timestamped checkpoints, follower checkpoint advance, cursor search paths, and disaggregated layered pages. Risks include insufficient eviction preventing fast-delete coverage and cursor-direction edge cases. Test signals are counts, exact landed keys, and timestamped visibility assertions.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate02.py -->
