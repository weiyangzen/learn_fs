# sources/storage-engines/foundationdb/bindings/python/fdb/locality.py

Purpose: This module exposes Python locality helpers for shard boundary discovery and storage-server address lookup.

Important APIs and types: `get_boundary_keys(db_or_tr, begin, end)` returns an iterator over shard boundary keys. `get_addresses_for_key(tr, key)` is transactional and returns a `FutureStringArray` from `fdb_transaction_get_addresses_for_key`. The private `_get_boundary_keys` generator implements retry and paging behavior.

Control flow: Inputs are normalized with `_impl.keyToBytes`. If called with a transaction, boundary scanning creates a separate transaction at the caller's read version; otherwise it creates a new transaction from the database. The scan reads system key range `\xff/keyServers/<begin>` to `\xff/keyServers/<end>` with read-system-keys and lock-aware options, yields once early to dispatch asynchronously, then yields decoded boundary suffixes.

State and persistence behavior: It does not persist user state. It reads FoundationDB system keys and may create replacement transactions after `transaction_too_old` if progress has already been made, which can make a long scan non-transactional after retry.

Dependencies and integration points: It depends directly on `fdb.impl` transaction, key conversion, `FDBError`, and future wrappers. `unit_tests.py` validates locality consistency by comparing addresses for shard starts and preceding end keys.

Risks: Boundary scans require system-key access and assume system key encodings with a fixed 13-byte prefix. The retry path can trade strict transactionality for progress. Address lookup requires an initialized C API symbol and valid transaction pointer.

Test signals: Python unit tests call `get_boundary_keys` and `get_addresses_for_key` with read-system-keys enabled and assert address sets are internally consistent across adjacent boundaries.
