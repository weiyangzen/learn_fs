<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_attr.h -->
# sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_attr.h

Purpose: `fuse_attr_t` is a C ABI attribute struct mirroring most kernel FUSE inode metadata: inode, size, blocks, timestamps with nanoseconds, mode, link count, ownership, device, block size, and padding.

Important behavior: this header is a lightweight wrapper and does not include conversion functions. It is used by `fuse_direntplus_t` and higher-level reply construction where attributes are packed near directory entries.

State and integration: the struct owns no memory and is copied into protocol buffers. It differs slightly from `struct fuse_attr` in `fuse_kernel.h`, where the final field is `flags`; here it is `_padding`, so conversion code must be explicit about which ABI is being used.

Risks and test signals: field-order and size drift can corrupt FUSE replies. ABI size/offset static assertions and readdirplus/getattr integration tests are useful.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_attr.h -->
