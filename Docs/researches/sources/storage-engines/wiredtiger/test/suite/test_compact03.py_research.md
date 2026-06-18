# sources/storage-engines/wiredtiger/test/suite/test_compact03.py

Purpose: verifies compaction does not significantly reduce file size when overflow values remain at the end of the file, and that new normal values reuse freed middle extents without increasing file size.

Important APIs and types: `compact_util`, `make_scenarios`, `session.compact`, helper `truncate`, `populate`, `get_size`, and compact progress stats.

Control flow: create small-page table with many normal values, checkpoint and measure size, append overflow values, checkpoint and measure growth, delete or truncate the middle 90 percent of normal values, checkpoint, compact and verify size mostly unchanged, then reinsert normal values into the freed middle range and compact again.

State and persistence behavior: overflow pages at file end prevent effective file truncation despite rewritten middle pages. Freed middle extents should be reused by later inserts.

Dependencies and integration points: tests block manager compaction around overflow items and free extent reuse. Tiered hook is skipped due to occasional rollback errors.

Risks: sensitive to overflow thresholds and page allocation sizes. Assertions allow 10 percent leeway on size.

Test signals: size with overflow is greater than without; after compaction size remains at least 90 percent of overflow size; later inserts do not increase file size.
