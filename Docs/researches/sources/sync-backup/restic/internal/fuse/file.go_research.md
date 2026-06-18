# sources/sync-backup/restic/internal/fuse/file.go

Purpose: Implements FUSE regular file nodes backed by restic content blobs.

Important APIs: `file`, `openFile`, `newFile`, `file.Attr`, `file.Open`, `openFile.getBlobAt`, `openFile.Read`, xattr methods, and `Forget`.

Control flow and state: `Open` looks up every content blob size, builds cumulative offsets, and adjusts reported size if stored node size differs from blob total. `Read` handles empty files, binary-searches the starting blob for the requested offset, fetches blobs through a shared blob cache, slices the first blob by offset, and copies until the response buffer is full or content ends.

Dependencies and integration: Uses `anacrolix/fuse`, restic repository `LookupBlobSize`/`LoadBlob`, blob cache, `restic.BlobHandle`, `data.Node`, and xattr helpers.

Risks: Missing blob sizes fail open. Read correctness depends on cumulative-size indexing and response buffer sizing. Concurrent reads rely on the blob cache for synchronization. Link count is clamped to at least one because Windows backups may store zero.

Test signals: No direct tests in this subset; compile-time interface assertions and FUSE integration coverage elsewhere protect behavior.
