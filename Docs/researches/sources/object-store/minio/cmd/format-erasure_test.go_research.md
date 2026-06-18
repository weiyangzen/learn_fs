<!-- BEGIN_FILE_RESEARCH: sources/object-store/minio/cmd/format-erasure_test.go -->
# sources/object-store/minio/cmd/format-erasure_test.go

## Purpose
Unit and benchmark coverage for erasure format migration, validation, quorum selection, repair, and initialization scaling. It protects the disk metadata compatibility layer used by erasure startup and healing.

## Important APIs, types, and functions
- `TestFixFormatV3` verifies local repair of empty `Erasure.This`.
- `TestFormatErasureEmpty` checks detection of empty `This` while ignoring nil formats.
- `TestFormatErasureMigrate` validates V1-to-V3 migration and rejection of unknown backend/version.
- `TestCheckFormatErasureValue` exercises invalid metadata fields.
- `TestGetFormatErasureInQuorumCheck` validates quorum reference selection and strict format comparison failures.
- `getFormatErasureInQuorumOld` and benchmarks compare old hash-based quorum with current drive-count quorum.
- `TestNewFormatSets` verifies `newHealFormatSets` preserves deployment ID.
- Storage initialization benchmarks cover hundreds to thousands of endpoints.

## Control flow
Tests build synthetic format layouts, clone them across disk slots, mutate selected fields to simulate missing disks or corruption, and assert validation results. Migration writes an old `format.json` to a temp disk root, runs migration, then reads back the file to assert version, UUID, and set preservation. Benchmarks create large format arrays or endpoint lists and repeatedly run quorum or initialization code.

## State and persistence behavior
Several tests write temp `format.json` files and temporary disk directories, all under test-managed roots. Benchmarks allocate random disk paths. The tested persisted state is the JSON schema and its migration side effects.

## Dependencies and integration points
Depends on temp disk helpers, endpoint construction, JSON marshal/unmarshal, filesystem writes, SHA-256 for the old quorum implementation, and erasure format APIs from `format-erasure.go`.

## Risks and edge cases
Some invalid cases use intentionally synthetic formats that may not match all production invalid states. The quorum test checks loss of more than half the formats but does not cover same drive count with conflicting UUID matrix in current quorum selection beyond later `formatErasureV3Check` mutation cases. Benchmarks do not clean up all random disk paths in the shown helper.

## Test signals
Signals are exact success/failure of migration, repaired `This` UUID equality, invalid-value errors, strict mismatch failures for set count, set size, and UUID changes, `errErasureReadQuorum` when quorum is lost, deployment ID preservation in heal formats, and allocation/runtime benchmark metrics.
<!-- END_FILE_RESEARCH: sources/object-store/minio/cmd/format-erasure_test.go -->
