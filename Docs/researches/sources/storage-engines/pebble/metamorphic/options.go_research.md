# sources/storage-engines/pebble/metamorphic/options.go

## Purpose
`options.go` defines, serializes, parses, and randomizes the Pebble and test-only options used by metamorphic runs. It ensures every child run can persist an `OPTIONS` file, reconstruct a `TestOptions` value, and exercise a wide matrix of filesystem, compaction, WAL, iterator, remote-storage, value-block, and format-version behavior.

## Important APIs, Types, and Functions
- Constants `minimumFormatMajorVersion`, `defaultFormatMajorVersion`, and `newestFormatMajorVersionToTest` define the format-version range under test.
- `parseOptions` parses Pebble options plus `[TestOptions]` keys using `pebble.ParseHooks`, known key formats, filter policies, key schemas, and custom option parsers.
- `optionsToString` serializes Pebble options plus test-only fields and custom options.
- `defaultTestOptions` and `defaultOptions` build baseline options with mem FS, archive cleaner, key schema/comparer, block property collectors, bloom filter, ingest split default, value separation policy, and debug checking.
- `TestOptions` stores a `*pebble.Options`, replay thread count, retry policy, key format, custom options, and many test-only toggles.
- `CustomOption` allows external tests to serialize custom named options and hook close/open around DB restarts.
- `standardOptions` returns a fixed set of option variants.
- `RandomOptions` mutates a baseline into one randomized configuration.
- Utility functions include `expRandDuration`, `setupInitialState`, `filterPolicyFromName`, `randInRange`, and `randPowerOf2`.

## Control Flow and State
Serialized options are Pebble's `Options.String()` plus a `[TestOptions]` stanza. Parsing starts from defaults and lets unknown parse-hook entries toggle test-only behavior. Some toggles also update `pebble.Options` immediately, such as strict crashable FS, disk FS, block-property collector disablement, value block enablement, shared/external storage format requirements, secondary cache size, ingest split, excise enablement, delete-only compaction excises, and jemalloc size classes.

`RandomOptions` first optionally parses private options that are not exposed through public setters, then randomizes scalar Pebble options, closures, WAL failover, iterator stack, compaction heuristics, allocator classes, level options, compression, filter policies, FS mode, latency injection, thread count, ingest/delete/single-delete options, block properties, value blocks, remote storage, value separation, iterator tracking, EFOS seed, ingest splits, excise, delete-only compaction excises, and downloads. It calls `EnsureDefaults` at the end.

`setupInitialState` clones a prior run's `data` directory into the current FS while skipping archive/checkpoints/tmp, parses the previous OPTIONS file, and adjusts WAL recovery dirs so runs can switch between store-local WALs and separate WAL dirs or WAL failover.

## State and Persistence Behavior
Options are persisted as text `OPTIONS` files in each run directory and parsed by `RunOnce`. `setupInitialState` performs real VFS cloning from a previous on-disk state into the configured test FS. Default and random options choose between in-memory, crashable in-memory, and default disk filesystems; remote-storage toggles influence later object storage setup in `Test` and op behavior.

## Dependencies and Integration Points
The file integrates with Pebble options parsing/serialization, key formats and schemas, table filters, bloom/binaryfuse policies, WAL failover, VFS, remote storage options, value separation, sstable settings, and run orchestration in `meta.go`. Operation behavior in `ops.go` reads many `TestOptions` booleans to choose runtime code paths.

## Risks and Edge Cases
- Round-tripping closure-valued options requires tests to compare return values rather than function identity.
- Some booleans serialize only when true, and `parseOptions` panics if a test-only boolean is explicitly set to false.
- Random format versions must be raised when features require newer formats, such as shared objects, synthetic prefix/suffix, value separation, or virtual SSTables.
- WALDir and WAL failover compatibility during initial-state cloning is strict and returns errors on unexpected directory names.
- Random extremely small sizes improve coverage but can create many files; code adjusts L0 stop-write thresholds to reduce stalls.

## Test Signals
`options_test.go` validates initial-state cloning, full options round-trip for standard and random options, block property collector presence after `RunOnce`, and custom option parsing/serialization.
