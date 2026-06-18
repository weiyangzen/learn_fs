## sources/user-network-fs/go-fuse/fuse/pathfs/copy.go

Purpose: helper to copy a file between two pathfs filesystems through their public interfaces.

Important APIs/types/functions: `CopyFile(srcFs, destFs FileSystem, srcFile, destFile string, context *fuse.Context) fuse.Status`.

Control flow: open source read-only, get source attrs, create/truncate destination with source mode, then loop reading 128 KiB chunks and writing them at increasing offsets. Releases and flushes both files with defers. Short writes return `EIO`.

State and persistence: persists data into the destination filesystem; source is read only.

Dependencies and integration: uses `FileSystem.Open`, `GetAttr`, `Create`, and nodefs `File` read/write/flush/release APIs.

Risks and test signals: lacks sparse-file/xattr preservation and assumes offset writes succeed fully. `copy_test.go` covers basic overwrite behavior.
