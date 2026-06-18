# sources/storage-engines/rocksdb/table/table_factory.cc

Purpose: registers built-in table factories and implements string-based creation of `TableFactory` instances.

Important APIs/types/functions: `RegisterTableFactories` uses `std::once_flag` to register block-based, plain, and cuckoo table factories with the default `ObjectLibrary`. `TableFactory::CreateFromString` registers built-ins, then calls `LoadSharedObject<TableFactory>`.

Control flow: the first create call installs three factory lambdas; subsequent calls reuse the loaded registry. Each lambda fills a `std::unique_ptr<TableFactory>` guard and returns the raw factory pointer required by the object registry interface.

State and persistence behavior: process-global registry state is mutated once. No SST or DB persistent data is written.

Dependencies/integration points: integrates `rocksdb/convenience`, customizable/object registry utilities, and concrete table factory classes for block-based, plain, and cuckoo formats. Used by config parsing and tools that load table factories by name.

Risks: only these built-ins are registered here; custom factories require object library/shared-object mechanisms. Factory creation returns defaults, not caller-customized table options.

Test signals: indirectly covered by configuration and object registry tests. Tools such as `SstFileDumper` also rely on table factory identity strings.
