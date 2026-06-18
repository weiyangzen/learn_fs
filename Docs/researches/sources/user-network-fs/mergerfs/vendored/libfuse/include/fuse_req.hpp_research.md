<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_req.hpp -->
# sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_req.hpp

Purpose: `fuse_req_t` is the vendored request object used by low-level dispatch and replies. It bundles request context, session pointer, file descriptor, negotiated connection info, and an ioctl mode bit.

Important APIs: `fuse_req_alloc` and `fuse_req_free` allocate and release request objects. Fields expose `fuse_req_ctx_t ctx`, `struct fuse_session *se`, `int fd`, `fuse_conn_info_t conn`, and `ioctl_64bit`.

State and integration: request objects carry per-request identity and connection/session state from receive through reply. They are central to every `fuse_reply_*` call.

Risks and test signals: lifecycle is strict: use after reply/free or double-free can corrupt dispatch. Tests should cover allocation defaults, reply freeing behavior, delayed replies, and ioctl 32/64-bit flag propagation.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse_req.hpp -->
