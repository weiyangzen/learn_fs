<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_timeouts.h -->
# sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_timeouts.h

Purpose: `fuse_timeouts_t` holds entry and attribute cache timeout values as 64-bit integers.

Important behavior: high-level callbacks receive or fill this struct for operations that return entries or attributes, allowing the dispatcher to encode cache validity in replies.

State and integration: it is copied into reply payloads and owns no resources. It integrates with lookup, getattr, symlink, link, fgetattr, statx, and readdirplus paths.

Risks and test signals: timeout unit consistency matters; mismatched seconds/nanoseconds conversion can cause stale or uncached kernel entries. Tests should verify zero, short, and long timeout encoding.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_timeouts.h -->
