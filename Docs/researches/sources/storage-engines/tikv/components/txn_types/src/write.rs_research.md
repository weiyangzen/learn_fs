# sources/storage-engines/tikv/components/txn_types/src/write.rs

## Purpose
Implements TiKV MVCC write-record metadata stored in the write column family. A write record identifies the logical write type, start timestamp, optional short value, protected rollback state, overlapped rollback markers, GC-fence timestamps, last-change hints, and transaction source.

## Important APIs, Types, and Functions
`WriteType` maps Put/Delete/Lock/Rollback to byte flags and can be derived from lock types. `Write` is the owned record with constructors `new` and `new_rollback`, builder-style setters for overlapped rollback, last change, and transaction source, `parse_type`, and `as_ref`. `WriteRef<'a>` is the borrowed serialization view with `parse`, `to_bytes`, `pre_allocate_size`, `check_gc_fence_as_latest_version`, `is_protected`, and `to_owned`.

## Control Flow
Serialization writes a required one-byte write type and varint start timestamp, then optional fields in order: short value, overlapped rollback flag, GC fence, last-change tuple, and transaction source. Parsing reads the required header, then loops over tagged optional fields until data ends or an unknown tag appears, preserving forward compatibility by stopping on unknown bytes. GC-fence checking treats a nonzero fence at or before the read timestamp as invalid when the fenced newer version is missing.

## State and Persistence Behavior
`WriteRef::to_bytes` defines the durable byte layout of write CF values. Short values inline small payloads instead of requiring default-CF reads. Protected rollback records use short value `b"p"`. Overlapped rollback and GC fence metadata repair collisions between commit records and protected rollback records when commit timestamps are not globally unique.

## Dependencies and Integration Points
Uses `TimeStamp`, `LastChange`, `LockType`, shared short-value constants, TiKV number codec, and crate error types. The write bytes are consumed by MVCC readers, GC compaction filtering, CDC, TiFlash, and transaction cleanup paths.

## Risks
The optional-field byte namespace reuses `b'R'` for both rollback type and overlapped rollback optional flag; correctness relies on position in the record. Short-value parsing panics if the encoded length exceeds remaining bytes instead of returning a recoverable bad-format error. Unknown tags stop parsing, so field ordering is part of the compatibility contract. Incorrect GC-fence or last-change data can cause stale values to be served or too many versions to be scanned.

## Test Signals
Unit tests cover write type mapping, serialize/parse round trips for optional fields, bad input, unknown trailing bytes, protected rollback detection, and GC-fence validity. Further test signals should include malformed short-value length fuzzing, cross-version optional-field ordering, and integration reads across overlapped rollback plus GC compaction.
