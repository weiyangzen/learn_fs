# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/KeyMayExistTest.java

## Purpose

Integration coverage for probabilistic `keyMayExist` overloads, including optional value retrieval, column-family routing, sliced byte arrays, direct and heap `ByteBuffer` inputs, and non-UTF8 values.

## Important APIs, control flow, and dependencies

Setup opens a DB with two column families and builds a sliced key embedded inside prefix/suffix bytes. Tests call byte-array overloads with `Holder<byte[]>`, null holders, `ReadOptions`, CF handles, and direct `ByteBuffer` value buffers. ByteBuffer tests assert returned `KeyMayExist` enum, value length, and value-buffer position/limit behavior when the destination buffer has an offset or insufficient remaining capacity.

## State, persistence, risks, and test signals

Temporary DB state is written through puts; no reopen is needed. `keyMayExist` may be conservative, but with freshly inserted keys it should return true and often the value. Risks include holder not being nulled on miss, incorrect offset/length validation, direct-buffer position corruption, null value-buffer misuse, CF mismatch, and non-Unicode byte handling. Signals are value equality, false results for wrong CF or partial wrong keys, `BufferUnderflowException` in expected read paths, and `AssertionError` for null value buffers in ByteBuffer overloads.
