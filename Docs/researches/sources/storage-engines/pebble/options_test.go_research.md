# sources/storage-engines/pebble/options_test.go

## Purpose

`options_test.go` verifies the behavior defined by `options.go`: randomized test defaulting, target file-size computation, exact default OPTIONS serialization, compatibility checks, WAL recovery directory validation, parse/string round trips, validation errors, key category classification, compression/table-filter policy application, and static span policy lookup. It is the focused test companion for Pebble's configuration surface.

## Important APIs, Types, and Functions

- `(*Options).randomizeForTesting` installs a test logger, randomizes `FormatMajorVersion` when unset, optionally randomizes value separation policy for formats that support it, optionally enables iterator tracking, and then calls `EnsureDefaults`.
- `testingRandomized` is a helper wrapper used across tests in this package.
- `TestTargetFileSize` checks `Options.TargetFileSize` for L0, base-level-relative target sizes, and shifted base levels.
- `TestDefaultOptionsString` pins `runtime.GOMAXPROCS`, forces `IteratorStackV1`, and asserts the full string emitted by `DefaultOptions().String()`.
- `TestOptionsCheckCompatibility` checks comparer and merger compatibility, RocksDB-style options parsing, `nullptr` merger handling, WAL dir and failover secondary migration checks, and `ErrMissingWALRecoveryDir` values.
- `TestWALRecoveryDirValidation` verifies that stale/old secondary recovery directories do not have their stable identifiers validated unless they are the current secondary.
- `writeTestIdentifierToFile` writes a stable identifier fixture into a VFS file and syncs it.
- `testCleaner` is a custom cleaner used to test parse hooks.
- `TestOptionsParse` constructs customized options, serializes them, parses them into a new `Options` with `ParseHooks`, and compares the resulting string.
- `TestOptionsParseLevelNoQuotes`, `TestOptionsParseInvalidLevel`, and `TestOptionsParseComparerOverwrite` target level section parsing and unknown-comparer behavior.
- `TestOptionsValidate` covers validation errors for compaction concurrency, L0 thresholds, memtable size, memtable stop-write threshold, and missing WAL failover secondary FS.
- `TestKeyCategories` verifies point-key and range-key category labels.
- `TestApplyDBCompressionSettings` and `TestApplyDBTableFilterPolicy` ensure dynamic profile closures are reflected across levels.
- `TestStaticSpanPolicyFunc` is datadriven and checks span policy selection over parsed key bounds.

## Control Flow and State

The tests mostly construct `Options`, call `EnsureDefaults`, serialize with `String`, parse with `Parse`, or validate with `Validate`. The parse round-trip test deliberately sets many fields before defaulting, including WAL failover, level options, deletion pacing, compaction knobs, tombstone thresholds, file-cache shards, secondary cache size, and value separation policy. It then ensures that the serialized and reparsed forms match exactly while confirming non-serialized runtime state like `Cache` remains nil.

Compatibility tests pass previous OPTIONS strings directly to `CheckCompatibility`, checking both Pebble's `[Options]` section and RocksDB's `[CFOptions "default"]` mapping. WAL migration cases inspect typed errors with `errors.As` and compare the reported directory. The WAL recovery identifier test creates directories and identifier files in `vfs.NewMem`, then calls the unexported `checkWALDir` path to ensure only the current secondary directory validates IDs.

The key category tests build a `UserKeyCategories` partition with sorted upper bounds, then test both single-key classification and range classification that may span multiple categories. Static span policy tests parse datadriven command args into `SpanPolicy` ranges and query `MakeStaticSpanPolicyFunc` for each input bound.

## Persistence and Compatibility Behavior

The file treats the OPTIONS string as a persisted compatibility contract. `TestDefaultOptionsString` detects accidental serialization changes to defaults. `TestOptionsParse` verifies that a persisted string can reconstruct all parseable fields. `TestOptionsCheckCompatibility` encodes the most important persisted-safety checks: comparer and merger identity, previous WAL directories, failover secondary directories, RocksDB import compatibility, and the explicit recovery-dir requirement for locations that may still contain WALs.

`TestWALRecoveryDirValidation` is a nuanced persistence signal: old secondary directories may carry IDs from past configurations and should still be usable for recovery without matching the current secondary ID. The check only validates identifiers for the current secondary, preventing false-open failures during WAL failover migrations.

## Dependencies and Integration Points

The tests use `leaktest`, `require`, `datadriven`, `errors`, `vfs`, `wal`, `base`, `strparse`, `testkeys`, `testutils`, `block`, `bloom`, and `crstrings`. They directly exercise `Options`, `ParseHooks`, `Cleaner`, `WALFailoverOptions`, `ValueSeparationPolicy`, `DBCompressionSettings`, `DBTableFilterPolicy`, `UserKeyCategories`, and `SpanPolicyFunc`, and indirectly guard `Open` because these persisted options are read during database startup.

## Risks and Edge Cases

- `TestDefaultOptionsString` is intentionally brittle. Any intentional default or serialization change requires updating the full expected string and considering on-disk compatibility.
- Randomization in `randomizeForTesting` broadens coverage but can make failures seed-dependent through format versions, value separation, and iterator tracking.
- Parse hooks must preserve existing fields when hooks cannot resolve custom names; `TestOptionsParseComparerOverwrite` guards against niling a comparer on unknown input.
- WAL dir compatibility tests are safety-critical because accepting an omitted recovery dir can lose unflushed writes.
- Closure-backed compression and filter policies must capture per-level indices correctly and must respond to later profile changes.
- Category and span-policy helpers panic on invalid construction, so tests focus on valid mappings rather than recovery from invalid caller input.

## Test Signals

This file is itself the direct test signal for `options.go`. It provides exact default-output regression coverage, parser compatibility coverage, validation coverage, and targeted behavioral checks for policy helpers. It complements `open_test.go`, which verifies that these options behave correctly when persisted and used by real DB opens.
