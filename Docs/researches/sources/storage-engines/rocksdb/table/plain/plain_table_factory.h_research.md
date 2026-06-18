<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/plain/plain_table_factory.h -->
# sources/storage-engines/rocksdb/table/plain/plain_table_factory.h

Purpose: Declares the `PlainTableFactory` entry point and documents the plain table on-disk format, including key/value layout, plain vs prefix key encodings, and the sequence-zero value shortcut.

Important APIs and types: `PlainTableFactory` overrides `Name`, `NewTableReader`, `NewTableBuilder`, `GetPrintableOptions`, and `Clone`. It exposes `kClassName()` and static `kValueTypeSeqId0`. The constructor accepts `PlainTableOptions`.

Control flow: RocksDB uses this factory wherever a column family is configured for plain table format. It creates builders during flush/compaction output and readers when opening plain SSTs. The extensive header comment is effectively the format contract consumed by `plain_table_builder`, `plain_table_key_coding`, and `plain_table_reader`.

State and persistence: The factory stores plain table options such as user key length, Bloom bits, hash table ratio, index sparseness, huge page TLB size, encoding type, full scan mode, and store-index mode. The documented file format is persistent and compatibility-sensitive.

Dependencies and integration points: Depends on `rocksdb/table.h` and public factory hooks. It integrates with the plain table builder/reader implementation and public `PlainTableOptions` configuration.

Risks: Plain table is designed for mmap/tmpfs-like storage and lacks compression and checksums. Fixed user-key length must match actual keys unless variable-length mode is selected. Prefix encoding correctness depends on the prefix extractor and index sparseness. `kValueTypeSeqId0` is part of the persistent key encoding shortcut.

Test signals: Format compatibility tests for plain and prefix encodings, sequence-zero special-case decoding, fixed vs variable key lengths, reader/writer round trips through the factory, and option clone/configuration behavior.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/plain/plain_table_factory.h -->
