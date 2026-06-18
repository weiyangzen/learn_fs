<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/error_freebsd.go -->
# sources/user-network-fs/bazil-fuse/error_freebsd.go

Purpose: FreeBSD-specific mapping for the platform error meaning missing extended attribute.

Important APIs, types, and functions: defines `ENOATTR = Errno(syscall.ENOATTR)`, sets `errNoXattr`, and registers the errno name in `errnoNames`.

Control flow: package init installs the display name for `ErrNoXattr`.

State and persistence behavior: process-global errno name map is updated at init.

Dependencies and integration points: paired with `error_std.go` to expose platform-independent `ErrNoXattr`.

Risks and test signals: build tags select this on FreeBSD; tests should verify Getxattr missing-attribute responses use ENOATTR.
<!-- END_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/error_freebsd.go -->
