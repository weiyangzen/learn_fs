<!-- BEGIN_FILE_RESEARCH: sources/storage-engines/pebble/blob_rewrite.go -->
# sources/storage-engines/pebble/blob_rewrite.go

## Purpose
Implements Pebble's blob-file rewrite compaction: a compaction variant that rewrites a physical blob file under the same logical `BlobFileID`, omitting values that are no longer referenced by live SSTables. Unlike ordinary compactions, it does not rewrite table files; it rewrites the blob payload and applies a `VersionEdit` that remaps the blob file ID from the old disk file number to the new one.

## Important APIs, Types, and Functions
`pickedBlobFileCompaction` is the picker output and records the target blob file, the referenced version, referencing tables, and whether high-priority garbage heuristics selected it. `ConstructCompaction` refs the version and builds a `blobFileRewriteCompaction`. `blobFileRewriteCompaction` implements the internal `compaction` interface through `AddInProgressLocked`, `Execute`, `Info`, `UsesBurstConcurrency`, cancellation, tracing, labels, and metrics hooks. `DB.runBlobFileRewriteLocked` performs the actual rewrite outside `DB.mu`. `blobFileRewriter`, `blockHeap`, and `blockValues` combine per-SSTable blob-reference liveness encodings and drive `blob.FileRewriter.CopyBlock`.

## Control Flow
The picker constructs a compaction with a referenced manifest version. `Execute` announces begin events, calls `runBlobFileRewriteLocked`, then under manifest update checks that the target blob file ID still maps to the same physical file. If the mapping disappeared, the compaction is cancelled; if it changed, an assertion fires because only one rewrite for a given blob should run. On success it installs a `VersionEdit` deleting the old physical blob and adding the new physical blob for the same `FileID`, updates metrics and read state, and emits an end event. The lower-level rewriter builds a heap of `BlobRefLivenessEncoding` values from all referencing tables, groups encodings by blob block ID, unions live value IDs, and copies only live values into the output file.

## State and Persistence Behavior
Persistent state changes are confined to the new blob object, object-provider sync, and the manifest `VersionEdit`. The file uses a `block.BufferPool` to avoid polluting the block cache while reading liveness blocks. `bytesWritten`, iterator block-read stats, and burst-concurrency counters feed compaction accounting. On failure after creating an output file, the output is recorded as obsolete for deletion pacing. The old blob file is only logically deleted after the version edit is accepted.

## Dependencies and Integration Points
This code integrates with the compaction picker/scheduler, manifest versioning, `objstorage`, blob writer/rewriter code, SSTable readers, columnar blob-reference liveness blocks, event listeners, metrics, `deletepacer`, object I/O tracing, and pprof labels. It depends on `fileCacheHandle.withReader` for reading SSTables and on `manifest.Version.BlobFiles` for stable blob-ID mapping.

## Risks and Edge Cases
The correctness hinge is accurate liveness metadata in all referencing SSTables; missing or malformed liveness encodings can drop live blob values or fail the rewrite. The heap currently stores one item per SSTable block reference, which may be expensive for many references. Cancellation is only checked at manifest application, so the file may still do wasted rewrite work. `Execute` returns nil even after setting event `Err`, which relies on the outer compaction framework's expectations. The output must reduce value size or an assertion catches stale picker statistics. Cleanup uses the input size as an approximate failed-output deletion size.

## Test Signals
Covered by `blob_rewrite_test.go`: datadriven tests validate value-separation metadata and explicit rewrite behavior, and a randomized rewrite test repeatedly rewrites original and rewritten blob files while verifying original blob handles still fetch expected values from new physical files.
<!-- END_FILE_RESEARCH: sources/storage-engines/pebble/blob_rewrite.go -->
