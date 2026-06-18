# sources/sync-backup/kopia/snapshot/snapshotfs/dir_writer.go

Purpose: writes a `snapshot.DirManifest` as a repository object and returns its object ID.

Important APIs/types/functions: `WriteDirManifest`.

Control flow: creates an object writer with description `DIR:<relative path>`, directory object prefix `"k"`, and the requested compressor/metadata compressor. It JSON-encodes the manifest, calls `Result`, and returns the object ID.

State and persistence: persists directory metadata into the repository object store. The writer is deferred closed even after successful `Result`.

Dependencies and integration points: paired with `readDirEntries`, used by uploader and directory rewriter. Object prefix drives `IsDirectoryID` autodetection in `repofs`.

Risks and test signals: JSON encode or writer result failures leave no valid directory object. Compressor choice must match policy expectations. Integration tests that upload, browse, restore, and verify snapshots exercise this path indirectly.
