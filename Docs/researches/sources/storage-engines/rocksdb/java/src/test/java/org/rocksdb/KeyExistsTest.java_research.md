# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/KeyExistsTest.java

## Purpose

Integration coverage for exact key-existence APIs across default CF, explicit column families, `ReadOptions`, byte-array slices, and direct `ByteBuffer` keys.

## Important APIs, control flow, and dependencies

`before` opens a DB with default plus `new_cf`; `after` closes handles and DB. Tests use `put`, `delete`, `keyExists` overloads, `ReadOptions`, direct buffers, offset/length key slices, and `ExpectedException`. They verify that each key exists only in its own CF, deletes change existence to false, and out-of-range byte-array offsets throw.

## State, persistence, risks, and test signals

State lives in memtables/SSTs of a temporary DB; no reopen is required. The direct-buffer tests validate JNI reads of `ByteBuffer` position/limit without copying through arrays. Risks include CF-handle routing mistakes, stale existence after delete, direct-buffer address handling, and Java bounds validation. Signals are true/false existence assertions and `IndexOutOfBoundsException` for invalid slices.
