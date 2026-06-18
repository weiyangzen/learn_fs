# sources/storage-engines/rocksdb/db/output_validator.h

## Purpose
`output_validator.h` declares `OutputValidator`, a small helper for validating key/value sequences inserted into SST files. It checks ordering and can compute a rolling hash used to compare what was written with what is later read back.

## Important APIs, Types, And Functions
The constructor takes an `InternalKeyComparator`, an `enable_hash` flag, and an optional precalculated hash seed. `Add` validates and records each key/value pair. `CompareValidator` compares two validators by `GetHash`. `GetHash` exposes the current hash with a warning that it is not intended as a persisted format.

Private state includes the comparator reference, previous-key buffer, rolling `paranoid_hash_`, and `enable_hash_`.

## Control Flow
Callers construct one validator per output/read-back stream, call `Add` for every internal key and value in order, and optionally compare validators after both streams have been processed. The header leaves the validation implementation to `output_validator.cc`.

## State And Persistence Behavior
The class stores transient validation state only. `prev_key_` grows to hold the most recently observed internal key. The rolling hash can be seeded, enabling continuation or comparison with a known earlier state, but the comments explicitly avoid persistence guarantees.

## Dependencies And Integration Points
The header depends on `db/dbformat.h`, `rocksdb/slice.h`, and `rocksdb/status.h`. It integrates with compaction and SST creation/readback code that can supply internal keys, values, and an `InternalKeyComparator`.

## Risks
`CompareValidator` compares hashes only; a hash collision could theoretically hide differences. The hash is also gated by `enable_hash_`, so comparing validators with hashing disabled compares identical zero/default hashes and should only be done when hashing was intentionally enabled or seeded.

The comparator is held by reference, so it must outlive the validator.

## Test Signals
Tests or callers should see OK for sorted internal-key streams, corruption from `Add` for malformed or descending keys, and matching hashes for identical streams when hashing is enabled.
