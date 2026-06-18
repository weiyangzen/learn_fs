# sources/user-network-fs/samba/source4/ntvfs/posix/vfs_posix.h

Purpose: `vfs_posix.h` defines the shared private data model for the POSIX NTVFS backend. It is the contract consumed by the many `pvfs_*` files that implement path resolution, open/close, locking, xattrs, ACLs, notify, searches, and metadata mapping.

Important APIs, types, and functions: Major structs include `pvfs_state`, `pvfs_dos_fileinfo`, `pvfs_filename`, `pvfs_file_handle`, `pvfs_file`, `pvfs_search_state`, `pvfs_odb_retry`, and `pvfs_acl_ops`. It defines `PVFS_RESOLVE_*`, `PVFS_FLAG_*`, share option names such as `PVFS_EADB` and `PVFS_XATTR`, and default timing/allocation constants.

Control flow: The header has no execution flow, but it shapes backend flow by separating per-tree state, per-open-handle state, per-client-file state, and search state. `pvfs_file_handle` deliberately differs from `pvfs_file` to support DOS deny semantics where multiple logical opens can share one low-level fd.

State and persistence behavior: `pvfs_state` owns connection-wide open file/search lists, locking contexts, notify context, mangle context, optional EADB handle, flags, timing options, and ACL state. `pvfs_file_handle` tracks fd, opendb locking key, oplock, seek offsets, write-time delay state, and create options. Persistent effects are in files, xattrs/EADB, and Samba lock/open databases.

Dependencies and integration points: It includes generated `vfs_posix_proto.h` and `vfs_acl_proto.h`, NDR xattr definitions, NTVFS common types, wbclient, tevent, and system filesys declarations. The ACL ops table is the extension point for xattr and NFSv4 ACL modules.

Risks: This header is central ABI glue inside the backend; layout changes can ripple widely. The flags combine compatibility and security-sensitive behavior, and ambiguous fields such as `mode` or probabilistic `stream_id` need careful handling by callers.

Test signals: Build coverage should catch prototype and struct use regressions. Functional tests should indirectly exercise each state family: open handle sharing, write-time delayed updates, search cleanup, xattr/ACL toggles, stream handling, and permission override paths.
