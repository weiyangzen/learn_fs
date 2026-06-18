<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/libcap/cap/file.go -->
# sources/security-integrity/libcap/cap/file.go

## Purpose
File capability support for the Go package: read, write, remove, import, and export Linux `security.capability` data.

## Important APIs, Types, And Functions
Defines VFS capability wire structs, errors `ErrBadSize`, `ErrBadMagic`, `ErrBadPath`, `ErrOutOfRange`, `GetFd`, `GetFile`, `GetNSOwner`, `SetNSOwner`, `SetFd`, `SetFile`, `Import`, `Export`, `ExtMagic`, and `MinExtFlagSize`.

## Control Flow
`digestFileCap` parses little-endian v1/v2/v3 xattrs into `Set`. `packFileCap` converts `Set` into VFS xattr bytes, collapsing effective bits to the Linux legacy file-effective flag. Setters reject non-regular files, remove xattrs for nil sets, and use an O_PATH `/proc/self/fd` fallback when a file cannot be opened read-only.

## State And Persistence Behavior
Mutates file xattrs and optional namespace owner UID in `Set`. Import/export are in-memory and lossless except namespace owner is not exported. File xattr changes persist on disk.

## Dependencies And Integration Points
Uses Linux `getxattr`, `fgetxattr`, `setxattr`, `fsetxattr`, remove xattr syscalls, `/proc/self/fd`, and `fd.go` descriptor handling. Tested by `cap_file_test.go` and import/export tests.

## Risks And Edge Cases
Effective file capability storage is lossy by design. Symlink and special-file handling is security-sensitive. O_PATH fallback depends on procfs mount path. `MinExtFlagSize` is a mutable package global.

## Test Signals
Signals are xattr round trips, symlink rejection, nil removal, unreadable-file fallback, import/export size checks, and bad magic/size errors.
<!-- END_FILE_RESEARCH: sources/security-integrity/libcap/cap/file.go -->
