<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/badger/manifest.go -->
# sources/storage-engines/badger/manifest.go

## Purpose
This file implements Badger's `MANIFEST` file format and mutation logic. The manifest is the durable catalog of SSTable IDs, levels, encryption key IDs, compression type, and atomic table create/delete changes used to reconstruct the LSM tree on startup.

## Important APIs, Types, And Functions
`Manifest` holds level sets, table metadata, and creation/deletion counters. `TableManifest` stores level, `KeyID`, and compression. `manifestFile` owns the manifest file handle, append lock, current manifest snapshot, rewrite threshold, external magic, and in-memory flag. Public/internal APIs include `openOrCreateManifestFile`, `helpOpenOrCreateManifestFile`, `manifestFile.addChanges`, `ReplayManifestFile`, `applyManifestChange`, `applyChangeSet`, `newCreateChange`, and `newDeleteChange`.

## Control Flow
Opening creates a new manifest via `helpRewrite` if none exists and the DB is writable, or replays an existing file with `ReplayManifestFile`. Replay checks eight magic/version bytes, validates the external magic, then reads length+CRC-framed protobuf `ManifestChangeSet`s until EOF or a partial final record. Writable opens truncate to the last complete offset and seek to the end. `addChanges` marshals a changeset, locks appends, applies it to the in-memory manifest, either rewrites if deletion churn is high or appends length+CRC+payload, then syncs.

## State And Persistence Behavior
The manifest file begins with `B d g r`, two bytes of external magic, and the two-byte Badger magic version. Every following record is four bytes length, four bytes CRC32C, and a marshaled `pb.ManifestChangeSet`. Rewrite writes `MANIFEST-REWRITE`, fsyncs it, closes it for Windows rename compatibility, renames over `MANIFEST`, reopens, seeks to end, and syncs the directory. In-memory mode returns a no-op manifest file.

## Dependencies And Integration Points
The file depends on protobuf messages from `pb`, compression enums from `options`, file helpers from `y`, `syncDir`, and table metadata emitted by compaction and memtable flushes. `levels.go` consumes `Manifest.Tables` on startup and writes create/delete changes during compaction, L0 table addition, drop-tree, and drop-prefix operations.

## Risks And Edge Cases
This is a critical crash-recovery surface. Bad magic, unsupported Badger version, external magic mismatch, malformed length larger than file size, checksum mismatch, invalid operations, and duplicate creates fail open. Partial final records are tolerated by returning a truncation offset. Delete of an already-removed table is warned and removes the ID from all levels, which is tolerant but can mask duplicate delete sources. Applying changes before writing means an append/write/sync error leaves `mf.manifest` ahead of disk until close/reopen.

## Test Signals
`manifest_test.go` covers basic reopen visibility, magic/version/checksum corruption, rewrite after many deletes, and concurrent manifest compaction appends under injected slow sync. Level tests and compaction flows indirectly validate create/delete change application.
<!-- END_FILE_RESEARCH: sources/storage-engines/badger/manifest.go -->
