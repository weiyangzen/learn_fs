# sources/user-network-fs/nfs-ganesha/src/include/fsal_api.h

Purpose: This is the central object-oriented FSAL contract. It defines API versioning, request operation context, module/export/object/data-server operation vectors, and public base structs that every FSAL and stacked FSAL must honor.

Important APIs/types/functions: `FSAL_MAJOR_VERSION`/`FSAL_MINOR_VERSION` gate out-of-tree module compatibility. `struct req_op_context` is the thread-local operation envelope for credentials, client, export, paths, pNFS DS, protocol data, and conditional logging. `struct fsal_ops`, `struct export_ops`, `struct fsal_obj_ops`, and `struct fsal_pnfs_ds_ops` are the main vtables. `struct fsal_module`, `struct fsal_export`, `struct fsal_obj_handle`, `struct fsal_pnfs_ds`, and `struct fsal_ds_handle` are public bases embedded by private FSAL implementations. Inline helpers handle module and export-root reference counts.

Control flow: The core loads a module, calls module config/create-export hooks, then dispatches protocol operations through export and object vectors. Lookup/open/create paths instantiate `fsal_obj_handle` values with references already held. I/O uses `read2`/`write2` callbacks and `struct fsal_io_arg`; pNFS MDS/DS calls flow through layout and DS handle vectors.

State and persistence: The header encodes long-lived module/export/object parentage, refcounts, export stacking, FSAL lists, per-operation `op_ctx`, file handle conversion invariants, pNFS segment bookkeeping, and layout return/commit state. Persistent NFS identity depends on stable wire-to-host-to-key and handle-to-key behavior.

Dependencies and integration points: It includes FSAL types, pNFS, config parsing, SAL shared state, AVL trees, atomics, refcounted strings, client/export managers, and upcalls. Integrates with MDCACHE, NFSv3/v4/9P paths, pNFS, DBus stats, export reload, delegation transitions, and state management.

Risks: ABI changes require version bumps. Mismatched handle conversion breaks cache identity. Incorrect reference ownership can unload modules, exports, or objects too early. Attribute masks and ACL ownership are easy leak points. Async callbacks must preserve request state and not run forbidden backend operations in callback context.

Test signals: Exercise export load/update/unexport, root lookup, handle round trips, open/create variants, read/write callback paths, lock/delegation/share behavior, pNFS layoutget/return/commit, DS read/write/commit, reference-count shutdown, and stacked FSAL pass-through.
