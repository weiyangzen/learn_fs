# sources/storage-engines/wiredtiger/test/suite/test_layered_cursor05.py

Purpose: extensive `search_near` and iteration edge-case suite for follower layered cursors combining stable checkpoint data, local ingest writes, and tombstones.

Important APIs/types/functions: helper methods format keys/values, insert/remove on arbitrary session, `insert_stable` with leader checkpoint and follower advance, `insert_ingest`, `remove_ingest`, search-near check helpers, notfound checks, either-neighbor checks, and sorted forward/backward assertions. Uses cursor `search_near`, `next`, `prev`, and bounds.

Control flow: setup creates leader/follower layered tables. Tests cover empty tables, ingest-only odd keys, stable-only even keys, split stable/ingest complete keyspace, opposite-side stable/local neighbors, far neighbors, multiple local/stable neighbor arrangements, all-larger/all-smaller cases, exact key tombstoned from stable or ingest-only state, all-deleted tables, cross-table tombstone overrides, iteration after search_near, consecutive tombstone ranges, full forward/backward scans of interleaved data, local overrides of stable values, beyond-max searches, and bounded search/next through tombstones.

State and persistence behavior: stable data is checkpointed through leader and visible after follower pickup; ingest data and tombstones are follower-local. Correct behavior requires merging these sources while hiding deleted keys and preserving sorted cursor movement.

Dependencies/integration points: layered cursor merge logic, `search_near` return-code semantics (`-1`, `0`, `1`, `WT_NOTFOUND`), tombstone visibility, bounds, follower checkpoint pickup.

Risks: where both adjacent neighbors are valid, tests allow either result, matching WiredTiger semantics. The suite is broad but focused on string-formatted numeric keys.

Test signals: pass means `search_near` handles stable/ingest boundaries, tombstones, empty sets, and subsequent iteration without returning deleted or out-of-order keys.
