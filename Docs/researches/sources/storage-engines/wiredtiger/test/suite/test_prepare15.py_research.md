# sources/storage-engines/wiredtiger/test/suite/test_prepare15.py

## Purpose

Validates commit and rollback of prepared transactions containing update/tombstone combinations, including history-store interactions and in-memory variants.

## Important APIs, Control Flow, and State

The file parameterizes in-memory mode, key format, and transaction end. `test_prepare_hs_update_and_tombstone` commits value A, commits a tombstone, prepares value B plus remove, evicts with `ignore_prepare`, resolves commit or rollback, evicts again, and verifies the historical read at timestamp 20 returns A. `test_prepare_hs_update` commits A, prepares update+remove, evicts, resolves, verifies timestamp 20 still sees A, advances timestamps, writes C, evicts, and checks timestamp 70 sees not found only if the prepare committed. `test_prepare_no_hs` handles a prepared insert/remove with no historical base and expects not found regardless of resolution.

## Dependencies, Risks, and Test Signals

Dependencies include `WT_NOTFOUND`, scenarios, in-memory logging options, history-store visibility, and release eviction. Risks center on replacing on-disk keys with history-store content or tombstones when prepared operations resolve. Signals are timestamped reads across commit/rollback and eviction before and after resolution.
