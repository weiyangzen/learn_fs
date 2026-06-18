# sources/storage-engines/leveldb/db/dbformat.h

## Purpose
This header defines LevelDB's internal key format and constants used across the DB implementation.

## Important APIs, Types, And Functions
It declares `config` constants for level count, L0 compaction/slowdown/stop thresholds, max memtable compaction level, and read sampling period. It defines `ValueType`, `SequenceNumber`, `kMaxSequenceNumber`, `ParsedInternalKey`, `InternalKeyComparator`, `InternalFilterPolicy`, `InternalKey`, `LookupKey`, `AppendInternalKey`, `ParseInternalKey`, `ExtractUserKey`, and `InternalKeyEncodingLength`.

## Control Flow
Inline parsing requires at least eight suffix bytes, decodes the fixed64 tag, splits sequence and value type, and rejects unknown value types. `InternalKey` wraps encoded strings to discourage accidental bytewise comparisons. `LookupKey` exposes three slices: memtable key with length prefix, internal key, and user key.

## State And Persistence Behavior
These definitions are on-disk contract. Internal keys are stored in tables and memtables and determine ordering, snapshot visibility, and deletion semantics. Config constants control compaction scheduling and write stall behavior, affecting persistent file layout but not file format.

## Dependencies And Integration Points
The header is included by DB implementation, memtable, version set, table cache, builders, iterators, filenames, dumps, and tests. It connects public comparators/filter policies to LevelDB internal data.

## Risks And Edge Cases
Changing enum values, sequence packing, comparator semantics, or max sequence would be format-breaking. `ExtractUserKey` asserts length >= 8, so callers must validate corrupted keys before extraction.

## Test Signals
`dbformat_test.cc` directly covers core encoding and comparator shortening. DB, corruption, and iterator tests exercise the same definitions under real storage operations.
