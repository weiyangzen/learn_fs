# sources/storage-engines/pebble/format_major_version.go

## Purpose
Defines Pebble's durable format-major-version system: version constants for backward-incompatible on-disk changes, table/blob format capability mapping, marker-file lookup and writing, runtime ratcheting, and migrations that mark or compact files before enabling newer invariants. It is the central gate that prevents older binaries from opening databases written with newer durable formats.

## Important APIs, Types, And Functions
`FormatMajorVersion` implements `String` and `SafeValue`. Constants run from `FormatDefault` through `FormatNewest`/`internalFormatNewest`, with `FormatMinSupported` set to `FormatFlushableIngest` and shared-object support starting at `FormatVirtualSSTables`. Methods include `resolveDefault`, `MaxTableFormat`, `MinTableFormat`, `MaxBlobFileFormat`, `DB.FormatMajorVersion`, `DB.TableFormat`, `DB.BlobFileFormat`, `DB.shouldCreateShared`, `DB.RatchetFormatMajorVersion`, `ratchetFormatMajorVersionLocked`, `finalizeFormatVersUpgrade`, `writeFormatVersionMarker`, `compactMarkedFilesLocked`, `findFilesRowblk`, and `markFilesForCompactionLocked`. `formatMajorVersionMigrations` maps each supported version to an idempotent migration closure.

## Control Flow
Opening a DB uses `lookupFormatMajorVersion` to locate the atomic `format-version` marker, parse the decimal version string, and reject unknown or unsupported versions. Ratcheting checks read-only state, version direction, unknown versions, and concurrent ratchets, then walks one version at a time. Each migration runs under `DB.mu`, performs any prerequisite work, and must call `finalizeFormatVersUpgrade`, which moves the marker, stores the new in-memory version atomically, and emits the format-upgrade event. Some migrations are simple finalizers; others compact already-marked files or mark row-block tables for compaction before finalizing.

## State And Persistence Behavior
The active format version is durable in an atomic marker named `format-version`, encoded as a stable decimal string. `d.mu.formatVers.vers` mirrors that durable state in memory. Ratcheting can mutate the MANIFEST by marking files for compaction through `VersionEdit.TablesMarkedForCompaction`, can wait for compactions to rewrite marked files, and can trigger event listeners. `findFilesRowblk` reads table formats through the file cache and identifies non-columnar data blocks for migration marking.

## Dependencies And Integration Points
This file depends on `atomicfs.Marker`, `vfs`, `manifest.VersionEdit`, compaction scheduling/conditions, file-cache reader access, `sstable.TableFormat`, `blob.FileFormat`, remote shared-object policy, block format inspection, and DB event listeners. Its gates are consumed by ingest, WAL writing, table writing, blob value separation, virtual SSTables, excise bounds records, shared objects, and compaction picking.

## Risks And Edge Cases
Format constants must never be renumbered because marker values are persisted. `FormatDefault` must not be written to disk. `MinTableFormat` is intentionally conservative for CockroachDB raft-log ingestion compatibility. Migrations that wait for compaction drop `DB.mu` through condition waits and must handle DB closure. `markFilesForCompactionLocked` requires `FormatMarkForCompactionInVersionEdit`; ordering of migrations is therefore significant. Unknown future versions and unsupported old versions must fail loudly to avoid corruption.

## Test Signals
`format_major_version_test.go` checks stable numeric values, migration coverage, ratcheting through all versions, persisted marker reopen behavior, unknown marker rejection, and table/blob format mappings. Integration signals include successful opens at requested formats, correct table/blob writer formats, format-upgrade event firing, and compaction of marked files during migrations.
