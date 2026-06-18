<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate11.py -->
# sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate11.py

Purpose: tests follower fast-truncate range specification: NULL start/end, full table, single-key truncates, empty gaps, invalid ordering, and open-ended behavior after later appends.

Important APIs/types/functions: uses `LayeredFastTruncateConfigMixin`, `concat`, `range_inclusive`, `wiredtiger.WiredTigerError`, `assertRaisesWithMessage`, and scenarios for native layered and table-layered URIs.

Control flow: each case creates a follower with specified keys, calls `truncate` with one range shape, and checks `visible_keys`. `test_truncate_with_start_greater_than_end` expects `/Invalid argument/`, rolls back the session, and verifies all rows remain. The open-ended append case truncates 80-end, then populates 200-210 and verifies those later keys survive.

State and persistence behavior: open-ended bounds are resolved against the visible table at commit time. Empty gaps do not alter state; invalid ranges must fail without partial effects.

Dependencies/integration points: integrates API-level `session.truncate` argument validation with layered visibility and follower ingest writes. Risks include off-by-one errors and inconsistent rollback state after an invalid truncate. Test signals are exact key arrays and specific WiredTiger error matching.
<!-- END_FILE_RESEARCH: sources/storage-engines/wiredtiger/test/suite/test_layered_fast_truncate11.py -->
