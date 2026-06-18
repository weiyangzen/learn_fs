<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/error_std.go -->
# sources/user-network-fs/bazil-fuse/error_std.go

Purpose: common, platform-independent exported missing-xattr error.

Important APIs, types, and functions: exposes `const ErrNoXattr = errNoXattr` and compile-time interface assertions for `error`, `Errno`, and `ErrorNumber`.

Control flow: no runtime control flow; platform files provide `errNoXattr`.

State and persistence behavior: no mutable state.

Dependencies and integration points: used by filesystem implementations responding to Getxattr/Listxattr/Removexattr and backed by Linux or FreeBSD errno constants.

Risks and test signals: incorrect platform mapping causes wrong kernel errno for absent xattrs. Build matrix tests are the main signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/error_std.go -->
