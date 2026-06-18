# sources/sync-backup/kopia/snapshot/snapshotfs/dir_reader.go

Purpose: parses a serialized Kopia directory object from JSON.

Important APIs/types/functions: `directoryStreamType` and `readDirEntries`.

Control flow: `readDirEntries` decodes a `snapshot.DirManifest` from an `io.Reader`, checks `StreamType == "kopia:directory"`, and returns entries plus summary.

State and persistence: read-only; it interprets repository object bytes opened by `repofs` and `dir_rewriter`.

Dependencies and integration points: paired with `WriteDirManifest`, used by `repositoryDirectory.loadLocked` and `DirRewriter.processDirectory` to materialize directory contents.

Risks and test signals: any schema or stream type change must preserve this validation. Errors distinguish invalid JSON from wrong stream type, which helps diagnose corrupt or misidentified objects. Coverage is mostly through repository filesystem and tree walker tests.
