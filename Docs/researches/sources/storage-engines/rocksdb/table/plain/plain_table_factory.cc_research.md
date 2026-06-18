<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/rocksdb/table/plain/plain_table_factory.cc -->
# sources/storage-engines/rocksdb/table/plain/plain_table_factory.cc

Purpose: Implements the plain table factory, options parsing/printing, and legacy memtable factory string parsing helpers.

Important APIs and functions: Defines option metadata for `PlainTableOptions`, implements `PlainTableFactory` constructor, `NewTableReader()`, `NewTableBuilder()`, `GetPrintableOptions()`, `GetPlainTableOptionsFromString()`, `GetPlainTableOptionsFromMap()`, `NewPlainTableFactory()`, plain table property-name constants, and memtable factory parsing helpers `GetMemTableRepFactoryFromString()` plus `MemTableRepFactory::CreateFromString()` overloads.

Control flow: The constructor registers configurable options. `NewTableReader()` calls `PlainTableReader::Open()` with table options and reader options. `NewTableBuilder()` ignores `skip_filters` and returns a `PlainTableBuilder`. Option string parsing maps text to `PlainTableOptions` through the configurable object framework and normalizes unsupported/not-found errors to invalid argument. Memtable factory parsing lazily registers built-in factories once in the default object library, extracts an ID/options map, and constructs the selected factory.

State and persistence: `PlainTableFactory` stores `table_options_`. Static option metadata and one-time object-library registration are process-global configuration state. Plain table property constants are persisted into SST user-collected properties.

Dependencies and integration points: Integrates with RocksDB configurable utilities, object registry, plain table reader/builder, memtable rep factories, string utility parsing, and public `NewPlainTableFactory` API.

Risks: `NewTableReader()` ignores its `ReadOptions` parameter directly and relies on table reader options. Built-in memtable registration in this file is broader than plain table and must remain compatible with legacy option strings. The unsupported `cuckoo` memtable intentionally returns null with an error message. `GetPrintableOptions()` uses fixed buffers and format macros.

Test signals: Options string/map parsing, printable options stability, factory clone/configure behavior, builder/reader construction with all plain table options, unsupported cuckoo memtable parsing, vector/skiplist/hash memtable URI variants, and error normalization to invalid argument.
<!-- END_FILE_RESEARCH: sources/storage-engines/rocksdb/table/plain/plain_table_factory.cc -->
