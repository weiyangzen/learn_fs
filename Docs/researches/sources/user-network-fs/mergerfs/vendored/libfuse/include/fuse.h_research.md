<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse.h -->
# sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse.h

Purpose: This is the high-level public API for the vendored FUSE layer. It defines `struct fuse_operations` callbacks used by mergerfs, declares setup/teardown/event-loop functions, and exposes cache/passthrough helpers.

Important APIs and types: `fuse_operations` covers path and file-handle operations including `getattr`, `readlink`, namespace mutation, xattrs, directory iteration, `read`, `write`, `copy_file_range`, `setupmapping`, `removemapping`, `syncfs`, `tmpfile`, and `statx` variants. `fuse_backing_id_is_valid` validates passthrough backing IDs. Public functions include `fuse_new`, `fuse_destroy`, `fuse_exit`, config accessors, `fuse_loop_mt`, `fuse_main`, `fuse_setup`, `fuse_teardown`, cache invalidation, garbage collection, and passthrough open/close.

Control flow and state: callers provide operation tables; the implementation mounts `/dev/fuse`, initializes sessions, dispatches kernel requests to callbacks, and sends replies. Request identity is passed through `fuse_req_ctx_t`. Persistent state lives in the opaque `struct fuse`, sessions, file handles, node caches, and backing IDs.

Risks and test signals: callback signatures must match the dispatcher exactly, especially newer extensions such as passthrough and statx. Missing callbacks may translate to `-ENOSYS` or default success depending on operation. Tests should mount a small filesystem and exercise high-level operations, multithreaded loop behavior, invalidation, passthrough ID lifecycle, and teardown after interrupts.
<!-- END_FILE_RESEARCH: sources/user-network-fs/mergerfs/vendored/libfuse/include/fuse.h -->
