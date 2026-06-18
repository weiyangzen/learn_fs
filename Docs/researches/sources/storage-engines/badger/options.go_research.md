<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/options.go -->
# sources/storage-engines/badger/options.go

## Purpose
This file defines Badger's main `Options` struct, defaults, table-option derivation, LSM-only mode, superflag parsing/serialization, and fluent option setters.

## Important APIs, Types, And Functions
`Options` includes directory, sync, versioning, read-only, logging, compression, in-memory, metrics, goroutine count, LSM sizing, value-log sizing, compaction, encryption, checksum, cache, conflict detection, namespace, external magic, and internal managed/test-only fields. `DefaultOptions` provides production defaults. `buildTableOptions` converts DB options into `table.Options`. `LSMOnlyOptions` raises value threshold. `parseCompression`, `generateSuperFlag`, and `Options.FromSuperFlag` handle string configuration. Numerous `WithX` methods return modified option values.

## Control Flow
Callers start with `DefaultOptions` or `LSMOnlyOptions`, then chain `WithX` methods. DB opening consumes the options and `buildTableOptions` supplies table builders/openers with current compression, checksum, cache, block, encryption, and allocation settings. `FromSuperFlag` generates a default map from current options, merges input flags, reflectively sets exported scalar fields, and specially parses compression strings such as `zstd:3`.

## State And Persistence Behavior
Options determine persistent layout and recovery behavior: `Dir`/`ValueDir`, value threshold, value-log file size, compression for new tables, encryption keys, checksum verification, external magic, LSM level sizing, and read-only/in-memory mode. Some options affect only new tables (`Compression`) while existing tables carry their own manifest/table metadata. `getFileFlags` maps read-only mode to file open flags.

## Dependencies And Integration Points
The file imports Badger `options` enums, `table.Options`, logger types, key registry usage through `buildTableOptions`, `z.SuperFlag`, and filesystem flags. Nearly every DB subsystem consumes this struct.

## Risks And Edge Cases
Reflection-based superflag handling excludes unexported or non-scalar fields and does not support logger/encryption key. `parseCompression` calls `y.Check` on bad numeric levels, which can panic rather than return an error. Some options are dangerous if misused: `BypassLockGuard`, wrong `ExternalMagicVersion`, managed transactions, or incorrect conflict detection settings. Changing size/threshold options affects compaction and storage behavior significantly.

## Test Signals
`options_test.go` verifies default options round-trip through superflag generation/parsing and special compression parsing for `zstd:2`. Broader tests exercise option effects indirectly through compaction, metrics, in-memory mode, read-only mode, managed mode, and close-time compaction.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/options.go -->
