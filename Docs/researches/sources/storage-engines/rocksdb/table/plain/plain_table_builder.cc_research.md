<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/plain/plain_table_builder.cc -->
# sources/storage-engines/rocksdb/table/plain/plain_table_builder.cc

Purpose: Implements `PlainTableBuilder`, the writer for RocksDB's plain table SST format optimized for mmap/in-memory files.

Important APIs and functions: Defines plain table magic numbers `kPlainTableMagicNumber` and `kLegacyPlainTableMagicNumber`, local `WriteBlock()`, constructor/destructor, `Add()`, `Finish()`, `Abandon()`, `NumEntries()`, `FileSize()`, checksum accessors, and `SetSeqnoTimeTableProperties()`.

Control flow: Construction initializes table properties, key encoder, optional index builder, Bloom/index metadata, DB/session/host IDs, and internal table property collectors. `Add()` parses the internal key, rejects range deletions, records prefix/full-key hashes for optional Bloom, encodes the key through `PlainTableKeyEncoder`, adds a prefix index entry, varint-encodes value length, appends the value, updates offsets and table properties, and notifies collectors. `Finish()` writes optional Bloom and plain table index meta blocks, writes the properties block, writes the metaindex block, then appends a footer with no checksum and the plain table magic number.

State and persistence: Persistent output is one data region followed by optional Bloom/index blocks, properties block, metaindex block, and footer. Runtime state tracks arena allocation, options, property collectors, Bloom builder, index builder, file writer, current offset, status/io status, table properties, key encoder, hashes, prefix extractor, and `closed_`.

Dependencies and integration points: Uses plain Bloom/index/key coding, meta block builders, footer builder, table property collectors, writable file writer, prefix extractor, internal key parsing, DB host ID reification, and RocksDB table builder interface.

Risks: Plain table does not support range deletions, compression, or checksums. Offsets are asserted to fit in 32 bits. `Finish()` has staged writes where partial files can exist on IO error. Index/Bloom emission only happens when `store_index_in_file_` and entries are present. Property collector errors are logged but do not stop the build.

Test signals: Build empty and non-empty plain tables, fixed and variable user-key lengths, plain and prefix encoding, range deletion rejection, index-in-file and no-index modes, Bloom bits per key zero/nonzero, collector callbacks, IO failure after each block write, footer magic compatibility, and checksum accessor forwarding.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/plain/plain_table_builder.cc -->
