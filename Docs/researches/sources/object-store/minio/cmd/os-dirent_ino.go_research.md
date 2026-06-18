# sources/object-store/minio/cmd/os-dirent_ino.go

## Purpose
This platform-specific helper returns an inode identifier from `syscall.Dirent` on Linux and Darwin platforms where the field is named `Ino`.

## Important APIs, Types, and Functions
- Build tags: `(linux || darwin) && !appengine`.
- `direntInode(dirent *syscall.Dirent) uint64` returns `dirent.Ino`.

## Control Flow
There is no branching. The function directly reads the inode field from the supplied directory entry.

## State and Persistence Behavior
The function is pure and has no persistence side effects.

## Dependencies and Integration Points
It depends on `syscall` and pairs with `os-dirent_fileino.go` for BSD platforms. Callers use `direntInode` as a portable abstraction over platform-specific `Dirent` field names.

## Risks and Edge Cases
The build tag excludes App Engine and assumes `Dirent.Ino` is available on the selected platforms. A nil pointer would panic. Porting to platforms with different field names requires another build-tagged implementation.

## Test Signals
No direct tests are present. Compile success on Linux/Darwin and directory traversal behavior provide indirect validation.
