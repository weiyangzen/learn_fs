<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/cmount/fs.go -->
# sources/user-network-fs/rclone/cmd/cmount/fs.go

## Purpose

`fs.go` adapts rclone's VFS layer to the cgofuse `FileSystemInterface`, implementing file, directory, stat, read/write, metadata, symlink, and error translation callbacks for `cmount`.

## Important APIs, Types, and Functions

`FS` stores the VFS, backing Fs, mount options, readiness channel, handle table, mutex, and destroyed flag. `NewFS` constructs it. Handle helpers `openHandle`, `getHandle`, and `closeHandle` map FUSE file handles to `vfs.Handle` objects. Callback methods include `Init`, `Destroy`, `Getattr`, `Opendir`, `Readdir`, `Statfs`, `OpenEx`, `CreateEx`, `Truncate`, `Read`, `Write`, `Flush`, `Release`, `Unlink`, `Mkdir`, `Rmdir`, `Rename`, `Utimens`, `Symlink`, `Readlink`, `Getpath`, and no-op or ENOSYS methods for unsupported operations. `translateError`, `translateOpenFlags`, and `getMode` bridge error codes, flags, and file modes.

## Control Flow

FUSE invokes callbacks concurrently. Most paths resolve a VFS node or parent directory, perform the VFS operation, translate errors to negative FUSE errno values, and log through `log.Trace`.

## State and Persistence Behavior

In-process state is the handle table and destroyed flag. Persistent effects are remote/VFS mutations for create, write, truncate, delete, rename, mkdir, rmdir, symlink, and modtime changes. Unsupported chmod/chown/access/fsync paths are no-ops.

## Dependencies and Integration Points

It depends on `mountlib`, `fs`, `fserrors`, VFS nodes/handles, cgofuse, and OS file modes. It is instantiated by `mount.go` and must satisfy cgofuse interfaces.

## Risks and Test Signals

Risks include handle-table races or leaks, off-by-one bad handle checks, direct-IO behavior for unknown sizes, Readdir offset incompatibility, errno mismatches, Windows timestamp filtering, unsupported xattrs/hardlinks, and no-op permission semantics. Tests should run VFS mount suites, concurrent open/read/write/release cases, error translation tables, directory listing with long names, modtime boundaries, and symlink support.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rclone/cmd/cmount/fs.go -->
