# sources/storage-engines/rocksdb/table/adaptive/adaptive_table_factory.cc

Purpose: implements `AdaptiveTableFactory`, which can read multiple SST table formats while delegating writes to a configured table factory.

Important APIs/types/functions: constructor, `NewTableReader`, `NewTableBuilder`, `GetPrintableOptions`, and `NewAdaptiveTableFactory`.

Control flow: constructor fills missing factories with plain, block-based, and cuckoo defaults, and defaults writes to block-based. `NewTableReader` reads the SST footer, checks the table magic number, and dispatches to the matching factory. `NewTableBuilder` delegates directly to `table_factory_to_write_`.

State and persistence behavior: stores shared table factory pointers. It reads SST footer metadata but does not persist data itself; writes are delegated.

Dependencies and integration points: depends on table format magic numbers, `ReadFooterFromFile`, `TableFactory`, `RandomAccessFileReader`, and `WritableFileWriter`. It integrates with DB/table options where adaptive table support is selected.

Risks and test signals: unknown magic numbers return `NotSupported`; footer read failures propagate. Mixed-format DB/table tests and options-printing tests are useful.
