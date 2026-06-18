<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_req_ctx.h -->
# sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_req_ctx.h

Purpose: `fuse_req_ctx_t` is a C ABI snapshot of the FUSE input header fields relevant to filesystem operations.

Important fields: it stores length, opcode, unique request ID, node ID, uid, gid, pid, and umask. These values are passed into high-level operation callbacks.

State and integration: the struct owns no memory and is valid as request metadata. It decouples mergerfs callbacks from raw `fuse_in_header` while preserving caller identity and permission context.

Risks and test signals: incorrect uid/gid/pid/umask propagation can break permission handling. Tests should exercise create/mkdir/mknod umask paths, idmapped invalid uid/gid behavior, and callback-visible request identity.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_req_ctx.h -->
