# sources/storage-engines/foundationdb/bindings/ruby/lib/fdblocality.rb

Purpose: This module implements Ruby locality helpers for storage-server address lookup and shard boundary iteration.

Important APIs and types: `FDB::Locality.get_addresses_for_key(db_or_tr, key)` returns a `FutureStringArray`. `get_boundary_keys(db_or_tr, bkey, ekey)` returns an `Enumerator` over decoded boundary keys.

Control flow: Address lookup wraps the call in `transact`. Boundary lookup creates a transaction or read-version-aligned transaction, sets system-key and lock-aware options, scans `\xff/keyServers/`, yields suffixes, and handles `transaction_too_old` by creating a new transaction after partial progress or calling `on_error` otherwise.

State and persistence behavior: It reads system-key metadata but does not persist user data. Long boundary scans can lose strict transactionality after progress and retry.

Dependencies and integration points: It depends on `fdbimpl` C functions, transaction options, `FutureStringArray`, and `FDB.strinc`-style key handling. Ruby tester locality tests exercise it.

Risks: The fixed system key prefix length and system-key access assumptions must match FoundationDB internals. In the transaction branch, `tr.set_read_version db_or_tr.get_read_version` passes a future-like object unless coercion is implicit, so this path is sensitive to Ruby lazy future conversion.

Test signals: Ruby tester `test_locality` verifies boundary key addresses are consistent across shard start/end points.
