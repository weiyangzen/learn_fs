<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_entry.h -->
# sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_entry.h

Purpose: `fuse_entry_t` stores cache metadata for a looked-up node: node ID, generation, entry timeout, attribute timeout, and nanosecond timeout parts.

Important behavior: it is a lightweight C ABI struct used in local response helpers and `fuse_direntplus_t`. It does not contain the attributes themselves.

State and integration: the struct is copied into response buffers and integrates with lookup/readdirplus cache handling. It owns no external resources.

Risks and test signals: node ID/generation semantics are kernel-visible; reuse bugs can break NFS/export support or cache invalidation. Tests should exercise lookup cache timeout encoding and generation stability.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_entry.h -->
