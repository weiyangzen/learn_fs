# sources/storage-engines/wiredtiger/test/suite/test_prepare16.py

## Purpose

Tests prepared commit and rollback across many keys when each key can occupy its own leaf page, for both in-memory and disk-backed trees.

## Important APIs, Control Flow, and State

The test configures large cache, small leaf pages, and large values, parameterizing in-memory mode, key format, and commit/rollback. It prepares 1000 inserted keys at timestamp 11, then uses a second session with `ignore_prepare=true` and `release_evict` to search every key and force page eviction while prepared. The transaction commits at timestamps 20/30 or rolls back. Stable advances to 30, disk-backed runs checkpoint, and a read at timestamp 20 expects all values on commit or `WT_NOTFOUND` on rollback.

## Dependencies, Risks, and Test Signals

Dependencies are timestamped transactions, release eviction, page sizing, and `WT_NOTFOUND`. The risk is page-by-page prepared resolution differing across many leaf pages or in-memory mode. Signals are full-range eviction and full-range timestamp verification after resolution.
