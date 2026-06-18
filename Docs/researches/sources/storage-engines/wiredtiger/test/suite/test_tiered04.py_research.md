# sources/storage-engines/wiredtiger/test/suite/test_tiered04.py

## Purpose
`test_tiered04.py` is a broad basic tiered-storage API test. It verifies `flush_tier`, local retention, per-object metadata, statistics, reconfiguration, forced flushes, and restart behavior.

## Important APIs, Types, and Functions
The class uses `TieredConfigMixin`, `get_conn_config`, `get_check`, `wiredtiger.stat`, and metadata cursors. Helpers include `check_metadata(uri, val_str)`, `get_stat(stat, uri)`, and `check(tc, base, n)`. The connection config sets `tiered_storage=(...,local_retention=3)`.

## Control Flow
The test creates a default tiered table, a tiered table with explicit bucket/prefix/retention, and a local non-tiered table. It writes records, calls checkpoint with `flush_tier=(enabled)` repeatedly, observes skipped and switched counts, waits for local retention, forces tier processing, checks local object removal, writes through open cursors, validates metadata for `tiered:`, `tier:`, `file:`, and `object:` URIs, tests statistics, reconfigures retention, exercises timeout/sync/force options, restarts, and verifies post-restart flush behavior.

## State and Persistence Behavior
It covers local `.wtobj` lifecycle, bucket object creation, metadata fields such as `last`, `oldest`, `tiered_object`, retention-driven local cleanup, and persistence of checkpoint/flush timing across restart.

## Dependencies and Integration Points
It integrates with schema creation, checkpoint manager, tiered manager worker units, statistics, metadata, directory-store buckets, and connection reconfiguration.

## Risks and Test Signals
The test is time-sensitive because retention cleanup is asynchronous. Signals include exact skip/switch/flush statistic values, object existence/removal checks, metadata substrings, and successful data verification after writes and restart.
