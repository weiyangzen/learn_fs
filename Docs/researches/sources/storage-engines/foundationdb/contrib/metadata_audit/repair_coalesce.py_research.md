# sources/storage-engines/foundationdb/contrib/metadata_audit/repair_coalesce.py

## Purpose
This script repairs uncoalesced `serverKeys` or `keyServers` metadata by deleting adjacent redundant entries while preserving the first key in each run. It is designed to be idempotent and supports dry-run inspection before destructive system-key edits.

## Important APIs, Types, And Functions
`decode_key_servers_value(v)` extracts source and destination storage server UID sets from serialized `keyServers` values after an 8-byte protocol header. `get_value_key(entry_type, value)` normalizes values for equality checks. `get_live_server_uids(db)` reads `serverList`. `read_entries_batched` scans metadata ranges in batches. `find_redundant_entries(entries, entry_type)` implements the coalescing algorithm. `delete_keys_batched` clears redundant keys. `coalesce_serverkeys` and `coalesce_keyservers` drive each repair type. `main` handles CLI, confirmation, lock acquisition, and summary.

## Control Flow
The CLI requires `--type serverKeys|keyServers` and either `--dry-run` or `--yes-i-am-sure`. Non-dry-run mode disables DD and takes MoveKeysLock via `fdb_metadata_utils`. For `serverKeys`, it reads live server UIDs, optionally filters by `--server`, scans each `\xff/serverKeys/<uid>` range, and deletes duplicate adjacent TRUE/FALSE entries. For `keyServers`, it scans `\xff/keyServers/` or a hex prefix and deletes adjacent entries whose decoded source/destination server sets match. A `finally` block releases the lock unless `--keep-dd-disabled` is set.

## State And Persistence Behavior
Dry-run mode reads only. Write mode mutates FDB system keys by clearing redundant entries under `serverKeys` or `keyServers`, and also writes MoveKeysLock/DD mode keys during lock lifecycle. Deletions are batched in transactions of 100 keys and each write transaction updates the MoveKeysLock write key.

## Dependencies And Integration Points
It depends on `fdb`, `argparse`, `struct`, `sys`, and shared metadata utility functions/constants. It integrates with FDB KRM semantics where each metadata key marks the start of a range and adjacent equal-value records are redundant.

## Risks And Edge Cases
This is destructive system-key repair. If `decode_key_servers_value` returns empty sets for malformed values, distinct corrupt entries may compare equal and be deleted. `serverKeys` processing only scans UIDs from `serverList` unless `--server` is supplied, so stale serverKeys for absent servers are not coalesced by default. `read_entries_batched` stores all entries in memory despite batching transactions. `--keep-dd-disabled` intentionally leaves cluster-wide DD disabled for chained repairs.

## Test Signals
Unit tests should validate duplicate-run detection, first-entry preservation, keyServers value decoding, malformed decode behavior, and batching range advancement. Integration tests should run dry-run and real repair on synthetic metadata in an isolated cluster, verify idempotency on second run, and confirm lock release/restored DD mode after success and exceptions.
