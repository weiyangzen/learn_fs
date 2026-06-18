<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_direntplus.h -->
# sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_direntplus.h

Purpose: `fuse_direntplus_t` combines entry cache metadata, inode attributes, and a directory entry for READDIRPLUS-style responses.

Important fields: `entry` is a `fuse_entry_t`, `attr` is a `fuse_attr_t`, and `dirent` is the variable-length directory entry tail.

State and integration: the struct is a packed response-building helper and owns no memory. It depends on the separate local ABI wrappers rather than directly using `struct fuse_entry_out`.

Risks and test signals: flexible-array layout means allocation size must include the filename and alignment padding. Tests should compare generated READDIRPLUS buffers against kernel FUSE expectations.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_direntplus.h -->
