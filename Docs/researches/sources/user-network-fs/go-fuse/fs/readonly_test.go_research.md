## sources/user-network-fs/go-fuse/fs/readonly_test.go

Purpose: verifies default read-only behavior for an empty inode tree and default permission modes for bare directory/file inodes.

Important APIs/types/functions: `TestReadonlyCreate` opens a non-existing file with `O_CREAT` and expects `EROFS`. `TestDefaultPermissions` creates child inodes with only file type bits and checks visible modes are directory `0755` and file `0644`.

Control flow: tests mount a root `Inode`, optionally populate children through `Options.OnAdd`, then use `unix.Open` or `syscall.Lstat` against the mount.

State and persistence: all state is in-memory inode metadata. No file data is written.

Dependencies and integration: validates default operation implementations and `StableAttr.Mode` normalization in the high-level `fs` package.

Risks and test signals: protects public API expectations for default nodes. Incorrect defaults can break simple read-only filesystems or permission-sensitive clients.
