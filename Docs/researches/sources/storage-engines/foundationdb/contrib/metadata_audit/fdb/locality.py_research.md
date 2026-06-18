# sources/storage-engines/foundationdb/contrib/metadata_audit/fdb/locality.py

## Purpose
This module provides locality helpers for the Python binding: boundary-key iteration for key ranges and storage-server address lookup for a key. These are low-level inspection utilities used to understand data placement.

## Important APIs, Types, And Functions
`get_boundary_keys(db_or_tr, begin, end)` returns a generator over boundary keys in `[begin, end)`. `_get_boundary_keys` performs the actual scan of `\xff/keyServers/<user-key>` system metadata. `get_addresses_for_key(tr, key)` is transactional and wraps `fdb_transaction_get_addresses_for_key` in a `FutureStringArray`.

## Control Flow
Boundary-key reads create a new transaction. If called with a transaction, the helper starts a separate transaction and copies the caller's read version to approximate consistency. It sets `read_system_keys` and `lock_aware`, scans the keyServers system subspace, yields `None` once to dispatch the first range before returning the generator, then yields stripped user boundary keys and advances by appending `b"\x00"`. Retryable errors are handled with `on_error`; a `transaction_too_old` after partial progress starts a new transaction and loses strict transactionality.

## State And Persistence Behavior
The module is read-only. It reads system keys under `\xff/keyServers/` and uses transaction options that permit system-key reads on locked databases. No persistent writes are issued.

## Dependencies And Integration Points
It depends on `fdb.impl` transaction classes, `keyToBytes`, and `FutureStringArray`. It integrates with the FDB C locality API for address lookups and with the keyServers metadata layout for boundary-key enumeration.

## Risks And Edge Cases
Boundary-key iteration is explicitly not guaranteed transactional after some `transaction_too_old` cases. It assumes the keyServers prefix string length when stripping `kv.key[13:]`; layout changes would break results. The generator returns no values when `begin >= end`. System-key reads require sufficient API version and transaction options.

## Test Signals
Tests should verify boundary keys for known split ranges, behavior with both `Database` and `Transaction` inputs, retry behavior across transaction-too-old cases, byte validation for begin/end, and address lookup returning a string array future for a populated key.
