# sources/storage-engines/rocksdb/table/block_based/block_based_table_factory.h

## Purpose
`block_based_table_factory.h` declares the public block-based SST table factory interface used by RocksDB to build and open block-based tables. It also declares `TailPrefetchStats`, a small shared runtime helper for adapting table-open tail prefetch sizes from recent open behavior.

## Important APIs, Types, And Functions
`TailPrefetchStats` exposes `RecordEffectiveSize(size_t len)` and `GetSuggestedPrefetchSize()`. Internally it stores `kNumTracked == 32` sample slots, a `port::Mutex`, and ring-buffer cursors `next_` and `num_records_`. The API is intentionally minimal: callers can record observed effective read lengths and ask for a suggested future prefetch size, with `0` meaning insufficient information.

`BlockBasedTableFactory` derives from `TableFactory`. Its constructor accepts `BlockBasedTableOptions` by const reference with a default-constructed default. `kClassName()` and `Name()` identify the factory as `kBlockBasedTableName()`, supporting RocksDB's checked-cast/configurable factory machinery.

The table construction API consists of `NewTableReader()` and `NewTableBuilder()`. The reader override accepts `ReadOptions`, `TableReaderOptions`, a `RandomAccessFileReader`, file size, destination `unique_ptr<TableReader>`, and a `prefetch_index_and_filter_in_cache` flag. The builder override accepts `TableBuilderOptions` and a `WritableFileWriter*`.

Configuration APIs include `ValidateOptions()`, `PrepareOptions()`, `GetPrintableOptions()`, protected `GetOptionsPtr()`, protected `ParseOption()`, and private `InitializeOptions()`. `IsDeleteRangeSupported()` returns true. `Clone()` returns a copy of the factory using `std::make_unique<BlockBasedTableFactory>(*this)`.

`tail_prefetch_stats()` exposes a pointer to the shared tail prefetch stats stored in `SharedState`. `SharedState` also carries a shared pointer to `CacheReservationManager`, allowing cloned factories to share cache memory reservation accounting for table readers.

The header declares extern metadata/property strings: `kHashIndexPrefixesBlock`, `kHashIndexPrefixesMetadataBlock`, `kPropTrue`, and `kPropFalse`.

## Control Flow
Consumers instantiate `BlockBasedTableFactory`, typically through the public RocksDB factory helper declared elsewhere and implemented in the `.cc` file. The factory is then used by column-family/table-building code through the virtual `TableFactory` interface. For reads, `NewTableReader()` opens an SST through the block-based reader implementation. For writes, `NewTableBuilder()` creates a block-based table builder.

Option lifecycle is exposed as prepare, validate, parse, and print hooks. `PrepareOptions()` normalizes and prepares options before validation/configuration use. `ValidateOptions()` rejects incompatible combinations with DB and column-family options. `ParseOption()` supports string/map configuration, and `GetOptionsPtr()` lets configurable infrastructure reach nested option objects such as block cache settings.

## State And Persistence Behavior
`table_options_` is the factory's owned option copy. It is the persistent configuration carrier from the factory's perspective, although individual option fields may point to external/shared objects such as caches, filter policies, or custom factories.

`shared_state_` is a `std::shared_ptr`, so a default copy or `Clone()` shares table-reader cache reservation state and tail prefetch history. This is significant for runtime behavior because cloned table factories are not independent for those adaptive/accounting components.

`TailPrefetchStats` state is volatile and synchronized. It is not serialized in table files or OPTIONS files, but it can affect later table opens while the process and shared factory state live.

## Dependencies And Integration Points
The header depends on RocksDB public table APIs (`rocksdb/table.h`), flush block policy APIs, DB/column-family option forward declarations, cache reservation management, port mutexes, and file reader/writer forward declarations.

Its main integration point is the `TableFactory` abstraction used by RocksDB column families. `BlockBasedTableFactory` is the concrete implementation for the default block-based SST format and connects option validation, reader creation, builder creation, delete-range support, and configurable object support.

## Risks And Edge Cases
The destructor is non-owning beyond standard smart-pointer fields and is declared empty. The builder API returns a raw `TableBuilder*`, so ownership transfer follows the `TableFactory` contract and callers must delete through the expected RocksDB ownership path.

`tail_prefetch_stats()` returns a raw pointer into shared state. The pointed object remains valid as long as the factory/shared state remains alive, but callers should not retain it past the owning factory graph lifetime.

`Clone()` shares `SharedState` because the default copy constructor copies `shared_state_`. This is intentional, but tests and callers should not assume clone isolation for table-reader cache reservations or tail prefetch stats.

## Test Signals
Header-level behavior is exercised through construction, clone, and virtual-interface tests. Useful checks include factory name/class name matching, delete-range support returning true, cloned factories sharing `tail_prefetch_stats()` behavior, default construction being usable without explicit options, and compile-time integration with `TableFactory::NewTableReader` overloads.

`TailPrefetchStats` should be tested for thread-safe recording, no-information return value, bounded sample retention, and stability after more than 32 records.
