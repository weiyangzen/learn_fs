<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/checkpoint.go -->
# sources/storage-engines/pebble/checkpoint.go

## Purpose
Implements `DB.Checkpoint`, which creates a filesystem snapshot of a Pebble database directory containing a consistent MANIFEST prefix, OPTIONS file, format marker, relevant SSTables/blob files, remote object catalog state, and WAL records truncated to the snapshot's visible sequence number.

## Important APIs, Types, and Functions
`CheckpointOption`, `WithFlushedWAL`, `WithRestrictToSpans`, and `CheckpointSpan` define the public options. `excludeFromCheckpoint` filters SSTables that do not overlap restricted spans. `mkdirAllAndSyncParents` creates the checkpoint directory and syncs newly created parents and the closest existing ancestor. `DB.Checkpoint` orchestrates snapshot construction. `copyCheckpointOptions` copies OPTIONS while commenting out the WAL Failover stanza. `DB.writeCheckpointManifest` copies record-aligned MANIFEST data and appends deletion edits for excluded files.

## Control Flow
`Checkpoint` rejects an existing destination. If requested, it writes synced empty log data to flush the WAL. It disables file deletion, locks the manifest, captures current version, format version, manifest file number/size, options number, virtual backing files, blob files, WAL list, flushable ingest files, and visible sequence number, refs the current version, then releases locks. It creates/syncs the destination, copies OPTIONS, writes the format marker, links or copies local table/blob files, records remote files for object-provider checkpoint state, appends manifest deletions for excluded tables/blobs, copies WALs through `wal.Copy` up to `visibleSeqNum`, syncs/closes the checkpoint directory, and removes the partial destination on error.

## State and Persistence Behavior
The implementation is crash-conscious: parent dirs are synced after creation, checkpoint files are written through a syncing FS, MANIFEST records are copied via `record.Reader`/`Writer`, marker directory sync happens before manifest marker movement, WALs are copied rather than linked, and the final checkpoint dir is synced. Version refs and disabled file deletion protect live physical files while copying. Restricted checkpoints rewrite manifest state to remove excluded SSTables and blob files.

## Dependencies and Integration Points
The code integrates with manifest/version state, virtual SSTable backing metadata, blob-file metadata, WAL manager/list/copy, object provider lookup and remote checkpoint state, VFS hard-link/copy behavior, atomic filesystem markers, OPTIONS parsing, flushable ingest replay, and Pebble format-version markers.

## Risks and Edge Cases
Restricted checkpoints are approximate: WALs and partially overlapping SSTs can still expose keys outside requested spans, and excluded SSTs can make some visible keys invalid relative to the full DB history. Shared/remote files depend on object-provider checkpoint state and in-memory references; comments warn shared file references may be lost after DB restart unless the checkpoint consumer handles that operationally. WAL copy must exclude writes after the captured visible sequence number. Manifest copying must remain record-aligned when appending deletion edits. Flushable ingest SSTs must be copied even if not yet in the LSM.

## Test Signals
`checkpoint_test.go` covers datadriven checkpoint/open/list/scan behavior, shared storage, options rewriting, concurrent checkpoint and compaction, WAL flushing through crashable memory, many-file restricted manifests crossing record boundaries, and pending flushable ingest regression coverage.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/checkpoint.go -->
