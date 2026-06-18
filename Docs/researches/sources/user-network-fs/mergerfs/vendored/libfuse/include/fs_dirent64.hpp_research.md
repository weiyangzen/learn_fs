<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/fs_dirent64.hpp -->
# sources/user-network-fs/mergerfs/vendored/libfuse/include/fs_dirent64.hpp

Purpose: This header defines `fs::dirent64`, a compact directory-entry record with inode, offset, record length, type, and flexible `name[]` storage.

Important API: `namelen()` returns `strlen(name)`, assuming `name` is NUL-terminated. The layout is used by `fuse_dirents.hpp` overloads to ingest filesystem directory entries into FUSE reply buffers.

State and integration: the struct is a view over variable-sized memory and owns nothing. It bridges lower-level filesystem directory records to the vendored FUSE dirent aggregation layer.

Risks and test signals: because `namelen()` scans until NUL, malformed or non-terminated records can overread. Tests should cover valid names, long names, and callers that pass explicit name lengths to avoid relying on implicit termination.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/fs_dirent64.hpp -->
