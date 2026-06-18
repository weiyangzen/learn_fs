# sources/storage-engines/rocksdb/db/seqno_to_time_mapping.h

## Purpose

`seqno_to_time_mapping.h` declares `SeqnoToTimeMapping`, the constants controlling mapping sizes, a helper for combining time-retention options across column families, and the fixed-trailer value packing APIs used by timed writes. The header documents the central approximation: a recorded pair means the timestamp is at or after that sequence number and before the next sampled sequence number.

## Important APIs, Types, and Functions

`SeqnoToTimeMapping::SeqnoTimePair` stores a `SequenceNumber` and Unix time, supports varint encoding/decoding, delta math, sorting, equality, and merge logic. Public mapping APIs configure `SetMaxTimeSpan` and `SetCapacity`, populate or append entries, switch through unenforced additions via `AddUnenforced`, decode/copy ranges, query proximal time or sequence bounds, encode to binary properties, and format a human-readable string. `MinAndMaxPreserveSeconds` combines `preserve_internal_time_seconds` and `preclude_last_level_data_seconds` settings and computes the sampling cadence. The packing functions add or parse a write-time or sequence-number trailer on a value.

## Control Flow

The class has two logical modes. Enforced mode promises sorted entries, nominal capacity, and time-span retention for external const queries. Unenforced mode allows historical or decoded data to be appended cheaply, deferring sort/merge/prune work until `Enforce` or `Append` reestablishes invariants. Query APIs require enforced mode and return sentinel values when no lower bound is known.

## State and Persistence Behavior

The state is a `std::deque<SeqnoTimePair>` plus `max_time_span_`, `capacity_`, and `enforced_`. Constants cap mappings at 100 pairs per SST and nominally 100 per CF, with a combined upper bound of 1000 when multiple CF settings interact. The header exposes debug-only inspection for tests but otherwise keeps the deque private.

## Dependencies and Integration Points

The header depends on RocksDB `Status`, `Slice`, `SequenceNumber`, and `dbformat` definitions. It is integrated by version/table metadata, column-family superversions, and time-aware compaction/tiering logic. `MinAndMaxPreserveSeconds` is designed for scanning CF options before choosing a global sample cadence.

## Risks and Test Signals

Risks include callers querying while unenforced, mixing sentinel zero with real data, capacity/time-span settings changing while entries are present, and trailer parse calls on too-short values. Test signals should assert API preconditions in debug builds, verify cadence rounding and disabled behavior, cover range-copy semantics, and ensure all packing helpers preserve value bytes and parse the expected trailer.
