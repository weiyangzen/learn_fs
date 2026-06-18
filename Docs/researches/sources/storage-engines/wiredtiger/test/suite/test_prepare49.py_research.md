# sources/storage-engines/wiredtiger/test/suite/test_prepare49.py

## Purpose

Tests eviction after rolling back a prepared transaction that updates, reserves, and deletes the same key.

## Important APIs, Control Flow, and State

With precise checkpoint and preserve-prepared enabled, the test commits a stable base value for key 1 at timestamp 5. It then begins a prepared transaction that updates key 1, calls `cursor.reserve()` on the key, and removes it, all under the same prepared transaction at timestamp 10 with prepared ID 1. Stable advances past the prepare timestamp to 15, then the transaction rolls back at timestamp 20. `_force_evict` opens a fresh session, reads key 1 at timestamp 5 with `ignore_prepare=true`, and resets a release-evict cursor to force eviction.

## Dependencies, Risks, and Test Signals

Dependencies are cursor reservation, prepared rollback, preserve-prepared config, timestamped read, and release eviction. The risk is reserve-in-the-middle chains confusing rollback/eviction resolution for update/delete prepared operations. The signal is eviction completing without crash while the base timestamp read succeeds.
