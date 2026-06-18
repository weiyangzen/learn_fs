# sources/storage-engines/leveldb/table/table_test.cc

## Purpose
`table_test.cc` is a broad behavioral test harness for blocks, tables, memtables, and DB iteration under shared iterator expectations.

## Important APIs, Types, and Functions
It defines `ReverseKeyComparator`, `StringSink`, `StringSource`, abstract `Constructor`, concrete `BlockConstructor`, `TableConstructor`, `MemTableConstructor`, `DBConstructor`, `KeyConvertingIterator`, and `Harness`.

## Control Flow
The harness inserts keys into a model map, builds the selected data structure, then checks forward scan, backward scan, and randomized seeks/next/prev operations. Test arguments vary structure type, reverse comparator, and block restart interval. Additional tests cover zero-restart blocks, randomized large DB data, memtable insertion, approximate offsets, and compressed offset estimates.

## State, Dependencies, and Integration
The test file stitches together table, block, DB, memtable, write batch, env temp directories, random data, and compression helpers. It uses in-memory table files for deterministic table tests and real DB files for merge integration.

## Risks and Test Signals
It is the strongest signal for iterator correctness across direction changes, custom comparator ordering, restart intervals, empty keys, special bytes, block boundaries, and compression. It does not deeply test corruption, but does test Java-compatible zero-restart blocks.
