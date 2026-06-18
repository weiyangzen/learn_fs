# sources/sync-backup/kopia/repo/format/content_format.go

## Purpose
Defines repository content-format parameters: hashing, encryption, ECC, secrets, master key, mutable pack/index/epoch settings, and password-change support.

## Important APIs, Types, And Functions
`ContentFormat` embeds `MutableParameters` and implements encryption, hashing, ECC, and format-provider parameter interfaces. `ResolveFormatVersion` applies defaults for format versions 1, 2, and 3. `MutableParameters` stores `Version`, `MaxPackSize`, `IndexVersion`, and `EpochParameters`; `Validate` enforces supported ranges.

## Control Flow
`ResolveFormatVersion` enables password change and index v2/epoch defaults for format v2/v3, and disables password change with index v1/no epoch for v1. `Validate` checks pack size bounds, index version bounds, and epoch parameter validity.

## State And Persistence
These structs are serialized into encrypted repository config inside `kopia.repository`. Sensitive fields are tagged for scrubbing by surrounding tooling.

## Dependencies And Integration Points
Depends on `epoch`, `units`, and `content/index`. The format manager and static provider use this type to construct hash functions, encryptors, content managers, and index-blob managers.

## Risks And Edge Cases
Unsupported format versions fail. Default resolution is separate from validation, so callers must ensure version-specific defaults are applied when needed. Pack size boundaries affect content packing, compaction, and performance.

## Test Signals
Format manager tests use these fields extensively for initialization, cache refresh, mutable parameter updates, retention updates, and password changes.
