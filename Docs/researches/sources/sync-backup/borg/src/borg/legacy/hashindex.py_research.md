# sources/sync-backup/borg/src/borg/legacy/hashindex.py

## Purpose
Implements reading and writing Borg 1.x repository index files that map 256-bit keys to 32-bit segment/offset pairs.

## Important APIs, Types, And Functions
Named tuples `NSIndex1Entry`, `NSIndex1EntryFormatT`, and `NSIndex1EntryFormat`. Class `NSIndex1` implements `MutableMapping` through `HTProxyMixin` and provides `iteritems`, `read`, `size`, `write`, `_read`, `_write_fd`, and `_read_fd`.

## Control Flow
Construction creates a `borghash.HashTableNT` with key size 32 and value size 8, optionally reading from a path. Writing emits a legacy header with magic, used entry count as entries/buckets, key size, and value size, then writes each key and raw value. Reading validates header length, magic, key/value sizes, expected file size, then scans bucket records, skipping empty and tombstone sentinel values before installing raw hash table entries.

## State And Persistence
The in-memory state is the `HashTableNT`. Persistent state is the binary legacy index format with magic `BORG_IDX`. Optional file wrappers can receive `hash_part("HashHeader")` callbacks.

## Dependencies And Integration Points
Used by legacy repository code. Depends on `borghash.HashTableNT` and modern `HTProxyMixin`.

## Risks And Edge Cases
Header validation is strict but key/value size checks are assertions. `size()` reports hash table memory sizing, not necessarily on-disk format size. `iteritems(marker)` starts yielding at the marker including it; callers must understand marker semantics. Empty/tombstone sentinels are detected by value prefixes.

## Test Signals
Legacy repository/hashindex tests should cover binary round-trip, invalid short file, bad magic, size mismatch, empty/tombstone buckets, marker iteration, non-string file objects, and hash header callbacks.
