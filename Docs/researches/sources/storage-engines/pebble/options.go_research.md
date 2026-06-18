# sources/storage-engines/pebble/options.go

## Purpose

`options.go` defines Pebble's public and internal configuration surface. It contains option structs for iterators, writes, levels, DB-wide behavior, WAL failover, value separation, span policies, compression, table filters, object storage, and user-key categorization. It also implements defaulting, OPTIONS serialization/parsing, compatibility checks against previously persisted options, validation, and conversion into lower-level sstable/blob/object-storage settings.

## Important APIs, Types, and Functions

- Public aliases expose internal/base and sstable types such as `SpanPolicy`, `ValueStoragePolicyAdjustment`, `TieringPolicy`, `UserKeyBounds`, `TableFilterPolicy`, `KeySchema`, `BlockPropertyCollector`, `BlockPropertyFilter`, `MaximumSuffixProperty`, `ShortAttributeExtractor`, and `UserKeyPrefixBound`.
- `IterKeyType` and `IteratorStack` enumerate iterator key modes and the legacy/V2 iterator implementation selection.
- `IterOptions` controls iterator bounds, point/range block filters, key types, range-key masking, durable-only reads, L6 filter use, stats category, tracking exemption, debugging, and internal iterator fields.
- `RangeKeyMasking` and `BlockPropertyFilterMask` support automatic point-key masking by range keys, optionally accelerated by suffix-aware block-property filters.
- `WriteOptions`, `Sync`, `NoSync`, and `GetSync` define per-write sync behavior.
- `LevelOptions` configures per-level block sizes, restart intervals, compression, filters, and index block size. `EnsureL0Defaults` and `EnsureL1PlusDefaults` fill defaults.
- `Options` is the main DB configuration struct. It spans cache, cleaner, comparer, debug checks, WAL behavior, open guard flags, event listeners, compaction knobs, read sampling, tombstone compaction, format major version, VFS, key schemas, locks, LSM sizing, logging/tracing, memtables, merger, concurrency, read-only mode, shared cache, block properties, remote storage, value separation, span policies, iterator tracking, table filters, flush delays, WAL recovery/failover, deletion pacing, allocator hints, unsafe options, and private test/internal knobs.
- `ValueSeparationPolicy`, `ValueStorageLatencyTolerant`, `ValueStorageLowReadLatency`, `SpanPolicyFunc`, and `MakeStaticSpanPolicyFunc` configure blob/value-placement policy by key span.
- `WALFailoverOptions.Validate` checks secondary WAL configuration.
- `DBCompressionSettings`, predefined compression profiles, `UniformDBCompressionSettings`, and `Options.ApplyCompressionSettings` configure compression across levels.
- `DBTableFilterPolicy`, progressive Bloom and binary-fuse filter profiles, `UniformDBTableFilterPolicy`, and `Options.ApplyTableFilterPolicy` configure filters per level.
- `Options.EnsureDefaults`, `DefaultOptions`, `WithFSDefaults`, `AddEventListener`, and `Clone` initialize and manipulate option values.
- `Options.String`, `parseOptions`, `ParseHooks`, and `Options.Parse` serialize and parse the OPTIONS file format, including RocksDB-compatible section/key mapping.
- `ErrMissingWALRecoveryDir`, `ErrSecondaryIdentifierMismatch`, `CheckCompatibility`, `checkWALDir`, `MakeStoreRelativePath`, `resolveStorePath`, and `validateWALRecoveryDirIdentifier` enforce compatibility and WAL recovery safety.
- `Validate`, `MakeReaderOptions`, `MakeWriterOptions`, `DB.makeWriterOptions`, `DB.makeBlobWriterOptions`, and `MakeObjStorageProviderSettings` translate validated options into runtime subsystems.
- `UserKeyCategories`, `UserKeyCategory`, `MakeUserKeyCategories`, `CategorizeKey`, and `CategorizeKeyRange` classify key ranges for informational labels.

## Control Flow and State

`EnsureDefaults` is the central defaulting path and is expected before validation and use. It fills cache size, comparer, cleaner, deletion pacing, ingest behavior, iterator stack, compaction concurrency, value separation policy, table filter decoders, key schema defaults, L0/level sizing, per-level defaults, logger/listener, manifest and file limits, memtable sizing, merger, format major version, filesystem wrappers, flush split bytes, WAL failover defaults, read sampling, tombstone thresholds, file-cache shards, multilevel compaction heuristic, span policy, virtual table rewrite threshold, and time functions.

`Options.String` serializes a stable OPTIONS representation with `[Version]`, `[Options]`, optional `[Value Separation]`, optional `[WAL Failover]`, and one `[Level "N"]` section per level. Private options are serialized only when true. Dynamic option functions are called at serialization time, so the persisted text captures current values rather than closures.

`parseOptions` scans the INI-like text line by line, maps RocksDB `CFOptions "default"` keys for comparer and merger compatibility, and delegates section/key handling through callbacks. `Options.Parse` uses this scanner to populate fields, parse durations/numbers/bools, invoke hooks for custom cleaner/comparer/filter/key-schema/merger implementations, tolerate unknown options with logging or `OnUnknown`, and reconstruct closure-backed fields for parsed values.

`CheckCompatibility` scans previous OPTIONS text for comparer, merger, WAL dir, and WAL failover secondary dir. It uses `checkWALDir` to ensure any previously relevant WAL directory is still current or listed in `WALRecoveryDirs`, unless unsafe missing-dir allowance is enabled. Identifier validation is only applied when a recovery dir matches the current secondary WAL directory, avoiding false failures for old secondaries.

`MakeStaticSpanPolicyFunc` builds a sorted, compacted boundary list from non-overlapping input spans, fills gaps with default policies, and returns a function that binary-searches by the requested start key to produce the span policy valid for that interval.

## Persistence Behavior

The serialized OPTIONS string is persisted to disk and later parsed for compatibility checks during open. Comparer and merger names are treated as compatibility-critical because changing them can make existing keys unreadable or incorrectly ordered. WAL directory history is also persistence-critical: if a previous primary or secondary WAL directory may contain unflushed logs, opening without listing it in current WAL locations or recovery dirs returns `ErrMissingWALRecoveryDir`.

`MakeStoreRelativePath` and `resolveStorePath` support portable WAL path encoding using `{store_path}`. `validateWALRecoveryDirIdentifier` reads `wal.StableIdentifierFilename` when available to protect against using the wrong current secondary disk.

Format major version defaulting is sensitive to shared objects: `FormatDefault` maps to `FormatMinSupported`, but `CreateOnShared` raises the default to the minimum format for shared objects. Validation also rejects incompatible `CreateOnShared` and format-version combinations.

## Dependencies and Integration Points

This file ties the public `pebble` package to many internal subsystems: `base` comparers, filters, key bounds, locks, and span policies; `cache`; `deletepacer`; `humanize`; `invariants`; `keyspan`; `manifest`; `objstorageprovider`; `remote`; `rangekey`; `sstable`, `blob`, `block`, `colblk`, `tablefilters`, `binaryfuse`, and `bloom`; `vfs`; `wal`; and `redact`. Runtime users include `Open`, iterator constructors, table readers/writers, blob writers, compaction/flush paths, WAL failover/recovery code, object storage providers, event listeners, file caches, and diagnostics.

## Risks and Edge Cases

- `Options` contains many closure-backed fields. Capturing loop indices correctly in `ApplyCompressionSettings` and `ApplyTableFilterPolicy` is essential; both functions copy the index before creating closures.
- `EnsureDefaults` mutates the receiver and can install wrappers around `FS`, including disk-health checking with a closer stored privately. Callers sharing `Options` must account for mutation.
- `Parse` intentionally tolerates many unknown fields for forward compatibility, but malformed known fields should fail. Overly strict parsing could break older/newer OPTIONS files; overly lax parsing could miss unsafe incompatibility.
- WAL directory compatibility is data-loss sensitive. Path resolution, `{store_path}` handling, secondary identifiers, and unsafe bypasses must remain conservative.
- `Validate` assumes defaults have already been applied. Calling it on raw options may produce misleading results or panic if closure fields are nil.
- User key categories require sorted upper bounds and a nil upper bound for the final category; invalid input panics.
- `MakeWriterOptions` panics if a selected key schema is missing. This is correct for internal invariants but means defaulting/validation must run first.

## Test Signals

`options_test.go` covers target file sizing, default string stability, parse/string round trips, RocksDB compatibility parsing, WAL recovery-dir compatibility, WAL identifier validation, invalid levels, validation failures, key categories, compression/table-filter policy closures, and static span policy behavior. `open_test.go` indirectly validates OPTIONS persistence, compatibility checks, WAL dir migration safety, and torn OPTIONS write handling.
