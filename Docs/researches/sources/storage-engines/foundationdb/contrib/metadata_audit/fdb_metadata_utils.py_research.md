# sources/storage-engines/foundationdb/contrib/metadata_audit/fdb_metadata_utils.py

## Purpose
This module centralizes shared constants and safety helpers for metadata audit scripts that read or write FoundationDB system metadata. It selects an API version, defines key prefixes for `serverKeys`, `serverList`, and `keyServers`, and implements MoveKeysLock management required before modifying key-range metadata.

## Important APIs, Types, And Functions
Constants include `SERVER_KEYS_PREFIX`, `SERVER_LIST_PREFIX`, `KEY_SERVERS_PREFIX`, matching end keys, `DD_MODE_KEY`, `MOVEKEYS_LOCK_OWNER_KEY`, `MOVEKEYS_LOCK_WRITE_KEY`, `SERVER_KEYS_TRUE`, and `SERVER_KEYS_FALSE`.

`take_movekeys_lock(db)` disables data distribution, records the previous DD mode, writes a random owner UID and write key, and returns the owner plus previous mode. `release_movekeys_lock(db, prev_dd_mode_value)` restores DD mode and randomizes lock keys. `update_movekeys_lock_write(tr)` updates the write key inside metadata write transactions. `set_write_transaction_options` and `set_read_transaction_options` apply access-system/read-system, lock-aware, timeout, and priority options. `_encode_dd_mode`, `_decode_dd_mode`, `_encode_uid`, and `strinc` support serialization and range boundaries.

## Control Flow
At import, the module attempts API versions `[740, 730, 720, 710, 700]` until one succeeds, failing hard if none do. Lock acquisition and release are transactional functions with system-key access and system-immediate priority. Metadata writers call `take_movekeys_lock`, perform batches while updating the lock write key, and call `release_movekeys_lock` in a `finally` path.

## State And Persistence Behavior
This module writes critical system keys: `\xff/dataDistributionMode`, `\xff/moveKeysLock/Owner`, and `\xff/moveKeysLock/Write`. Disabling DD has cluster-wide operational impact. It does not write KRM entries directly, but it prepares transactions that repair/restore scripts use to mutate `serverKeys`, `serverList`, and `keyServers`.

## Dependencies And Integration Points
It depends on the local `fdb` Python binding, `struct`, and `uuid`. `repair_coalesce.py` and `restore_metadata.py` import it. The comments tie behavior to FDB internal `MoveKeys.actor.cpp`, so correctness depends on current internal lock semantics.

## Risks And Edge Cases
Import-time API selection can mask version mismatches until a later operation fails. If a process dies after `take_movekeys_lock` and before release, DD may remain disabled or lock ownership stale. `_decode_dd_mode` is unused by current scripts but documents default handling. The custom `strinc` returns `key + b"\x00"` for all-0xff keys, which differs from some strict prefix-end expectations but is not used on all-0xff metadata prefixes.

## Test Signals
Unit tests can validate encoders, UID byte length, prefix end keys, and transaction option calls with fakes. Integration tests should run dry-run paths and, in an isolated cluster, verify lock acquisition disables DD, release restores previous mode, and each metadata write batch updates the lock write key.
