# sources/storage-engines/leveldb/include/leveldb/table_builder.h

Purpose: declares the writer for LevelDB table files, used by memtable flush, compaction, repair, and standalone table construction.

Important APIs and types: `TableBuilder`, `ChangeOptions`, `Add`, `Flush`, `status`, `Finish`, `Abandon`, `NumEntries`, `FileSize`, private `WriteBlock`, and `WriteRawBlock`.

Control flow: callers create a builder with a writable file, add keys in strictly increasing comparator order, optionally flush blocks, then call `Finish` or `Abandon` before destruction. `Finish` stops using the file but does not close it.

State and persistence behavior: writes persistent table blocks, index/meta blocks, filters, compression, and footer through the supplied file. File size is tracked as output grows.

Dependencies and integration: depends on `Options`, `WritableFile`, `BlockBuilder`, and compression settings. Used by `BuildTable` and repair table copying.

Risks and edge cases: failing to call `Finish` or `Abandon` before destruction violates the contract. Out-of-order keys corrupt table format assumptions. Only some options can change dynamically.

Test signals: indirectly covered by memtable flush, compaction, repair, and memenv DB tests.
