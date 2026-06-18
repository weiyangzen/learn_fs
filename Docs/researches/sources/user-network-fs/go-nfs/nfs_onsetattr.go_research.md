<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/go-nfs/nfs_onsetattr.go -->
# sources/user-network-fs/go-nfs/nfs_onsetattr.go

## Purpose
Implements NFS SETATTR, including optional ctime guard support and weak-cache-consistency response.

## Important APIs, Types, and Functions
`onSetAttr` is the handler.

## Control Flow
It reads a handle, resolves it, parses `SetFileAttributes`, lstat's the object, optionally reads and checks a guard ctime, validates write capability, applies changes through `Handler.Change`, then writes OK and WCC data.

## State and Persistence Behavior
Persistent state is metadata or size mutation of the backing object.

## Dependencies and Integration Points
Depends on `ReadSetFileAttributes`, `SetFileAttributes.Apply`, billy write capability, XDR, and WCC helpers.

## Risks and Edge Cases
Guard comparison depends on `FileTime` equality from current stat; `Apply` may return non-NFS errors for some paths; read-only filesystems reject after parsing guard.

## Test Signals
SETATTR tests should cover mode, uid/gid, size, atime/mtime, guard success/failure, symlink truncation rejection, and read-only behavior.
<!-- END_FILE_RESEARCH: sources/user-network-fs/go-nfs/nfs_onsetattr.go -->
