# sources/storage-engines/rocksdb/table/adaptive/adaptive_table_factory.h

Purpose: declares a `TableFactory` implementation that reads block-based, plain, or cuckoo tables adaptively.

Important APIs/types/functions: `AdaptiveTableFactory`, `Name`, `NewTableReader`, `NewTableBuilder`, `GetPrintableOptions`, and `Clone`.

Control flow: header defines the override surface and stores four factory pointers: one for writes and three read dispatch targets.

State and persistence behavior: state is only shared factory ownership. Persistence is handled by delegated table builders/readers.

Dependencies and integration points: included by options/table code that constructs adaptive factories; depends on RocksDB table and options interfaces.

Risks and test signals: `Clone` uses the default copy of shared pointers, so clone instances share underlying factories. Factory configuration and table-format compatibility tests matter.
