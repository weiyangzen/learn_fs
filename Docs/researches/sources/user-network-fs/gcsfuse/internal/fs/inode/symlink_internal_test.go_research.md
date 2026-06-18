# sources/user-network-fs/gcsfuse/internal/fs/inode/symlink_internal_test.go

Purpose: internal-package tests for private symlink inode helpers, especially generation-pinned reading and target resolution. The tests validate behavior that external symlink tests cannot reach, such as `openReader` and `resolveSymlinkTarget`.

Important fixtures: `SymlinkInternalTest` owns a background context, fake bucket, and simulated clock. `createSymlinkInode` creates a fake GCS object, converts it to `MinObject`, installs either legacy target metadata or standard symlink metadata plus body content, builds a `gcsx.SyncerBucket`, and calls `NewSymlinkInode`.

Control flow and state: `TestOpenReader` reads standard symlink content through `openReader`. `TestOpenReader_Clobbered` creates a symlink inode, rewrites the same object to change generation, and expects `openReader` to return an error wrapping `FileClobberedError`. `TestResolveSymlinkTarget_Standard` and `_Legacy` validate the two storage formats; `_Clobbered` verifies standard resolution maps stale generations to clobbered errors. Constructor tests cover legacy success, standard success, read error for a missing standard object, and invalid metadata returning `symlink target could not be resolved`.

Dependencies and integration: uses fake storage, `storageutil.CreateObject`, `storageutil.ConvertObjToMinObject`, `gcsx.NewSyncerBucket`, `fuseops`, and `gcsfuse_errors`. It is tightly integrated with GCS generation semantics and the symlink inode constructor path.

Risks: the helper mutates `MinObject.Metadata` after object creation rather than patching bucket metadata, so it tests inode construction from object records rather than a complete storage metadata update path. The tests do not assert reader close warning behavior or precedence when both legacy and standard keys are present.

Test signals: these tests are the main guard for stale-generation safety in symlink target reads and for maintaining both legacy and standard symlink compatibility.
