# sources/storage-engines/pebble/format_major_version_test.go

## Purpose
Validates the durable format-major-version contract: stable numeric values, complete migration definitions, ratcheting at open and while open, persisted marker behavior, rejection of unknown future versions, and exhaustive mappings from format major versions to supported table/blob formats.

## Important APIs, Types, And Functions
Tests include `TestFormatMajorVersionStableValues`, `TestFormatMajorVersion_MigrationDefined`, `TestRatchetFormat`, `testBasicDB`, `TestFormatMajorVersions`, `TestFormatMajorVersions_TableFormat`, `TestFormatMajorVersions_BlobFileFormat`, and `TestFormatMajorVersions_MaxTableFormat`. They call `Open`, `DB.RatchetFormatMajorVersion`, `DB.FormatMajorVersion`, `DB.TableFormat`, `FormatMajorVersion.MinTableFormat`, `MaxTableFormat`, `MaxBlobFileFormat`, and `atomicfs.LocateMarker`.

## Control Flow
Stable-value tests compare each exported/current format constant against explicit numbers. Migration coverage iterates from `FormatMinSupported` through `FormatNewest`. Ratchet tests open a memory DB, write data, ratchet through every version, close/reopen to verify persistence, then manually move the marker to `999999` and expect open failure. Exhaustive version tests create DBs at each version, run basic set/flush/compact/iteration operations, and use crash clones to test upgrade-at-open and upgrade-while-open without mutating the original filesystem. Format mapping tests iterate valid ranges and assert expected min/max table and blob formats, including panic checks for invalid versions.

## State And Persistence Behavior
The tests exercise real marker persistence in a memory filesystem and crash-cloned filesystems. `testBasicDB` writes and flushes data, compacts the full key range, and iterates through the resulting version, ensuring each format can sustain basic persistent operations. Marker tampering tests verify persisted unknown versions block open with a precise error.

## Dependencies And Integration Points
The file depends on `vfs.NewMem`, `vfs.NewCrashableMem`, `atomicfs`, `sstable.TableFormat`, `blob.FileFormat`, Pebble open/flush/compact/iterator APIs, and test logging. It provides direct coverage for the format gates used by table writing, blob file writing, ingest validation, WAL/manifest compatibility, and migrations.

## Risks And Edge Cases
Adding a new format version requires updating both stable-value expectations and mapping tables; otherwise tests fail. Crash clones are used to isolate upgrade permutations, reducing cross-test contamination. Invalid-version panic checks protect `resolveDefault` and format mapping code. The explicit marker move to an unknown version verifies Pebble does not silently downgrade or ignore future durable state.

## Test Signals
Signals include exact numeric constant equality, every supported version having a migration closure, successful basic DB operations across all versions and upgrade paths, persisted upgraded version after reopen, exact unknown-version error text, expected table/blob format mappings, and expected panics for unsupported mappings.
