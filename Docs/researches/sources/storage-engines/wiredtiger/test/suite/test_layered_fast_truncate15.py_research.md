<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate15.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate15.py

Purpose: validates that follower truncate tombstones only ingest keys inside the truncate range and does not tombstone flanking ingest keys.

Important APIs/types/functions: uses the shared mixin with `setup_leader`, `setup_follower`, `truncate`, `key_exists`, and `visible_keys`. Scenarios cover native layered and table-layered URIs.

Control flow: tests create small stable key sets with follower ingest keys below, above, or on both sides of a truncate range. After truncation, they check stable keys inside the range are hidden while ingest keys outside the range remain visible. One case checks the complete scan result `[0, 5, 25, 30]`.

State and persistence behavior: the ingest component may contain keys close to, but outside, the stable range being truncated. The truncate implementation must avoid over-eager tombstone writes beyond the bounds.

Dependencies/integration points: focuses on boundary handling in the follower truncate code that drains/marks ingest keys. Risks are off-by-one or cursor-position errors that tombstone adjacent ingest entries. Test signals are point existence assertions and one full visible-key scan.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate15.py -->
