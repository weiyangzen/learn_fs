## sources/user-network-fs/go-fuse/fuse/nodefs/memnode.go

Purpose: simple deprecated nodefs in-memory filesystem backed by temporary on-disk files for file content.

Important APIs/types/functions: `NewMemNodeFSRoot`, `memNodeFs`, `memNode`, `memNodeFile`, and methods for tree creation, filename mapping, mkdir/unlink/rmdir/symlink/rename/link/create/open/getattr/truncate/utimens/chmod/chown.

Control flow: filesystem allocates temp files under a prefix, creates nodes for directories/files/symlinks, and maps inode operations to temp file operations. `memNodeFile.Flush` syncs data back to node metadata as needed.

State and persistence: tree metadata is in memory; file contents are stored in temp files under the prefix and removed with lifecycle cleanup.

Dependencies and integration: used by nodefs examples/tests and POSIX-style validation of nodefs.

Risks and test signals: temp-file cleanup, rename/link bookkeeping, and metadata consistency are risk areas. `memnode_test.go` exercises core operations.
