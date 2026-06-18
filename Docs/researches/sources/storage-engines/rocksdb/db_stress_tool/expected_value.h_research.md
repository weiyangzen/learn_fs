# sources/storage-engines/rocksdb/db_stress_tool/expected_value.h

## Purpose
`expected_value.h` defines the compact expected-value representation for db_stress. It encodes existence, value generation, delete generation, and pending operation state in one 32-bit word so expected state can be stored as a dense atomic array.

## Important APIs, types, and functions
`ExpectedValue` exposes bit-mask metadata, constructors, `Exists()`, `Read()`, mutation APIs, value-base and delete-counter accessors, pending-bit accessors, deleted-bit accessors, and final-state helpers. `PendingExpectedValue` is an RAII-like token that owns an in-flight transition and must be closed by `Commit()`, `Rollback()`, or `PermitUnclosedPendingState()`. `ExpectedValueHelper` provides read-validation predicates for concurrent operations.

## Control flow
Callers typically load an `ExpectedValue`, derive pending and final variants, store the pending variant before writing the DB, and then use `PendingExpectedValue` to publish either the final or original value. Copy/move constructors and assignment close the source token's pending state to preserve the invariant that only one live token is responsible for assertion closure. The destructor asserts that pending state was closed.

## State and persistence behavior
The 32-bit layout is: bits 0-14 value base, bit 15 pending write, bits 16-29 delete counter, bit 30 pending delete, bit 31 deleted. Initial construction defaults to deleted. `Commit()` and `Rollback()` use a release fence before storing final or original raw values into the atomic pointer. This prevents expected-state publication from being reordered before the corresponding DB write boundary.

## Dependencies and integration points
The header depends on standard atomics and RocksDB namespace configuration. It is directly embedded in `ExpectedState` cells, used by validation helpers in db_stress operations, and interpreted by recovery trace replay.

## Risks and test signals
Because fields share one word, all setters must validate masked values and clear old bits before setting new ones. `Exists()` asserts no pending state, so callers must not use it for ambiguous concurrent windows. The copy/move behavior is unusual and should be tested because it mutates the source token's closure state. Tests should cover bitfield masks, wraparound, pending token commit/rollback, destructor assertions in debug builds, and helper behavior during pending writes/deletes.
