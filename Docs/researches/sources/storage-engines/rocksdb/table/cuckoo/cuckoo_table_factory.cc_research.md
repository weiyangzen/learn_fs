# sources/storage-engines/rocksdb/table/cuckoo/cuckoo_table_factory.cc

Purpose: implements the table factory that wires cuckoo table options into RocksDB table reader and builder creation.

Important APIs/types/functions: `CuckooTableFactory::NewTableReader`, `NewTableBuilder`, `GetPrintableOptions`, constructor option registration, and `NewCuckooTableFactory`.

Control flow: `NewTableReader` constructs a `CuckooTableReader` with immutable options, file, file size, user comparator, and no custom hash callback; it returns the reader only if its status is OK. `NewTableBuilder` constructs a `CuckooTableBuilder` using factory options, hard-coded max hash function count of 64, table-builder comparator/column-family metadata, DB/session IDs, and file number. `GetPrintableOptions` formats selected options for diagnostics.

State and persistence: the factory owns `CuckooTableOptions`. It does not write data itself, but builder creation determines persisted cuckoo layout parameters such as hash ratio, search depth, block size, module hash, and identity hash.

Dependencies/integration: depends on configurable options registration, option type metadata, `CuckooTableBuilder`, `CuckooTableReader`, and public `NewCuckooTableFactory` entry point. It implements `TableFactory` virtual methods used by DB/table creation.

Risks and test signals: `GetPrintableOptions` omits `use_module_hash`, despite registering it, so diagnostics may be incomplete. Reader ignores prefetch-index-and-filter flag because cuckoo format has different metadata behavior. The subset's builder tests do not directly instantiate the factory; factory coverage likely comes from options/table factory tests elsewhere.
