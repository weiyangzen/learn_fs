# sources/storage-engines/wiredtiger/test/suite/test_hs11.py

## Purpose

Tests how no-timestamp updates or deletions clear obsolete history-store records, and contrasts that with timestamped removals that should not clear HS content the same way.

## Important APIs, Types, and Functions

Defines a large scenario matrix over key format, update/deletion, long-running transaction, final modify, row count, and insert/update-list location. Helpers include `create_key`, `get_stat`, and `evict_cursor`.

## Control Flow

The first test writes timestamped versions 1-4, optionally evicts them, optionally adds a timestamp 5 modify and long reader, then applies no-timestamp changes to even keys, checkpoints, evicts, adds timestamp 10 updates, and reads historical timestamps. The second performs timestamped removals at 10 and verifies older visibility without HS truncation.

## State and Persistence Behavior

State includes HS records on insert or update lists, globally visible versus pinned no-timestamp updates, optional modify records, and statistic `cache_hs_key_truncate_onpage_removal`.

## Dependencies and Integration Points

Depends on `wiredtiger.Modify`, statistics, scenario generation, `wttest.transaction`, and debug eviction cursors.

## Risks and Maintenance Signals

The scenario matrix is large and mutates `self.timestamps` when modifies are enabled, which can be subtle across scenarios. It assumes even/odd key partitioning for expectations.

## Test Signals

Signals are historical read values/notfound outcomes at each timestamp and HS truncate stat greater than zero only for no-timestamp deletion clearing.
