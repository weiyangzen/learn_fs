<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_dirent.h -->
# sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_dirent.h

Purpose: `fuse_dirent_t` is a vendored directory-entry wire helper with inode, offset, name length, type, and flexible trailing name storage.

Important behavior: it is a C struct used to pack one directory record into a contiguous response buffer. Size and alignment are handled by surrounding code, usually using FUSE record alignment rules.

State and integration: the struct owns no memory; it is embedded in `fuse_direntplus_t` and appended to `fuse_dirents_t` buffers.

Risks and test signals: callers must allocate enough trailing storage and align records correctly. Directory listing tests should validate names, offsets, d_type values, and exact byte layout.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_dirent.h -->
