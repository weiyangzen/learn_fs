# sources/storage-engines/rocksdb/include/rocksdb/external_table.h

## Purpose

`external_table.h` declares an experimental plugin interface for using non-block-based table file implementations with RocksDB. External tables can be written through `SstFileWriter` and read through `SstFileReader`, with future ingestion into restricted RocksDB instances. The design supports total-order seek, prefix seek, or both.

## Important APIs, types, and functions

`ExternalTableIterator : public IteratorBase` adds `Prepare` for multi-scan planning, `NextAndGetResult`, `PrepareValue`, `value`, and `UpperBoundCheckResult`. `ExternalTableReader` creates iterators, serves `Get` and `MultiGet`, optionally returns a raw properties block, returns `TableProperties`, and optionally verifies checksums. `ExternalTableBuilder` writes sorted key/value pairs through `Add`, reports `status`, finalizes with `Finish`, cleans partial output with `Abandon`, returns `FileSize`, writes optional properties blocks, exposes table properties, and may expose whole-file checksum data.

`ExternalTableOptions` passes prefix extractor, comparator, filesystem, and file options to readers. `ExternalTableBuilderOptions` passes read/write options, prefix extractor, comparator, column family name, creation reason, and filesystem to builders. `ExternalTableFactory : public Customizable` creates readers and builders, and `NewExternalTableFactory` wraps it as a RocksDB `TableFactory`.

## Control flow and behavior

For writing, RocksDB calls `NewTableBuilder`, then `Add` in comparator order, checks `status`, and calls either `Finish` or `Abandon`. RocksDB owns final sync and close of the supplied `FSWritableFile`. For reading, RocksDB opens a reader, creates an iterator, optionally calls `Prepare` with scan options, seeks, iterates, and materializes lazy values through `PrepareValue` when needed. Point and batched lookups flow through `Get` and `MultiGet`.

## State and persistence

External table builders persist the table file and table properties. Minimum required properties are comparator name, entry count, raw key size, and raw value size. Optional raw properties blocks must be written as-is with returned offset and size. Optional checksums integrate with file checksum metadata using constants from `file_checksum.h`.

## Dependencies and integration points

The header depends on advanced iterator APIs, customizable, checksums, filesystem, iterator base, options, status, and table factory types. It integrates with `SstFileWriter`, `SstFileReader`, `ReadOptions`, `WriteOptions`, `SliceTransform`, `Comparator`, `FileSystem`, `FSWritableFile`, and `TableFactory` selection through column family options.

## Risks and test signals

The interface is explicitly experimental and subject to change. Correct key ordering is critical: total-order mode must obey the comparator globally, while prefix mode must maintain order within each prefix and honor `prefix_same_as_start`. Failure to return required properties can break metadata consumers. Lazy value preparation must be consistent with iterator validity. Tests should cover total-order and prefix seeks, forward/reverse iteration, `Prepare` reuse and interruption, `Get`/`MultiGet` status mapping, properties block round trips, checksum verification, `Abandon` cleanup, and not closing or syncing the file inside the builder.
