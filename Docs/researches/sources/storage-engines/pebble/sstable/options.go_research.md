# sources/storage-engines/pebble/sstable/options.go

## Purpose
Defines public reader/writer options, defaults, compression profile aliases, key-schema registries, tombstone-density defaults, and table-format compatibility checks.

## Important APIs, Types, and Functions
- Constants: `MaximumRestartOffset`, `DefaultNumDeletionsThreshold`, and `DefaultDeletionSizeRatioThreshold`.
- `ignoredInternalProperties` lists RocksDB internal properties not surfaced as user properties.
- `Comparers`, `Mergers`, `KeySchemas`, and `MakeKeySchemas`.
- `ReaderOptions.ensureDefaults` fills comparer, merger, logger/tracer, and key schemas.
- Compression profile aliases expose block compression settings.
- `WriterOptions` includes block sizing, comparer/compression/filter/index/key schema, table format, obsolete/tiering/blob/value/block-property options, cache/internal settings, and tombstone-density thresholds.
- `UserKeyPrefixBound.IsEmpty`, `JemallocSizeClasses`, `WriterOptions.SetInternal`, `WriterOptions.ensureDefaults`, and `tableFormatSupportsCompressionProfile`.

## Control Flow
Reader defaults are filled before opening tables. Writer defaults fill restart interval, block size, thresholds, comparer, index size, merger, checksum, table format, deletion thresholds, columnar key schema, compression fallback, and filter policy. Compression defaults fall back to Snappy if the selected profile is unsupported by the table format, such as MinLZ before v6.

## State and Persistence Behavior
Options influence persisted SSTable layout and metadata: table format, block sizes, compression, filters, key schema names, obsolete bit behavior, tiering metadata, value-block usage, block property collectors, and deletion-density properties. The options structs themselves are not persisted, but selected values are written into properties and footer/layout.

## Dependencies and Integration Points
Used by `NewReader`, `NewWriter`, `RawColumnWriter`, `layoutWriter`, and test helpers. Depends on `base`, `sstableinternal`, `block`, `colblk`, and `rowblk`.

## Risks and Edge Cases
`MakeKeySchemas` panics on duplicate names. Defaults depend on table format, so changing `TableFormat` after `ensureDefaults` can leave inconsistent key schema/compression choices. External use of `DisableValueBlocks` is specialized and can affect performance/format behavior. Tiering histogram options require matching getter/extractor functions.

## Test Signals
Indirectly covered across reader/writer tests, format tests, columnar writer tests, and option parsing tests outside this subset.
