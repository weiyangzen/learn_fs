<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/error_linux.go -->
# sources/user-network-fs/bazil-fuse/error_linux.go

Purpose: Linux-specific mapping for the platform error meaning missing extended attribute.

Important APIs, types, and functions: defines `ENODATA = Errno(syscall.ENODATA)`, assigns `errNoXattr`, and registers `ENODATA` in `errnoNames`.

Control flow: init updates the errno display table.

State and persistence behavior: only process-global errno name state changes.

Dependencies and integration points: consumed by `error_std.go` and xattr request handlers.

Risks and test signals: Linux syscall behavior must use ENODATA for absent xattrs; tests should assert `fuse.ErrNoXattr` encodes that value.
<!-- END_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/error_linux.go -->
