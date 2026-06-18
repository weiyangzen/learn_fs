# sources/storage-engines/rocksdb/java/src/test/java/org/rocksdb/MergeCFVariantsTest.java

## Purpose

Parameterized integration coverage for column-family merge overloads using `UInt64AddOperator`.

## Important APIs, control flow, and dependencies

The parameter list covers `RocksDB.merge` overloads with raw byte arrays, `WriteOptions`, array offsets/lengths, direct `ByteBuffer`, and heap `ByteBuffer`. The test opens a DB with default and `new_cf` using merge-operator CF options, puts an initial 64-bit value, applies the selected merge variant, reads and decodes the result, then creates another CF and verifies a normal merge there.

## State, persistence, risks, and test signals

Merge operands are stored in the DB and resolved through the configured CF merge operator. Risks include overload-specific JNI bugs, ByteBuffer position handling, offset/length mistakes, merge operator not attached to dynamically created CFs, and handle cleanup. Signals are exact numeric sums: `100 + 1 = 101` and `200 + 50 = 250`.
