# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_CEPH/internal.c

## Purpose

`internal.c` supplies Ceph FSAL shared helpers: object-handle construction/destruction, FSAL-to-Ceph attribute mask conversion, Ceph statx-to-FSAL attribute conversion, optional POSIX ACL xattr conversion, and the global AVL registry for shared `ceph_mount` objects. The complete 531-line file was read for this report.

## Important APIs, Types, and Functions

Important functions are `construct_handle`, `deconstruct_handle`, `attrmask2ceph_want`, `ceph2fsal_attributes`, `ceph_get_posix_acl`, `ceph_set_acl`, `ceph_get_acl`, `ceph_mount_key_cmpf`, `ceph_mount_init`, `ceph_mount_lookup`, `ceph_mount_insert`, and `ceph_mount_remove`. Global state is `struct avltree avl_cmount` and `pthread_rwlock_t cmount_lock`.

## Control Flow

`construct_handle` allocates a `ceph_handle`, copies inode/snap/fscid/export id into its key, stores the libcephfs inode pointer, initializes the public FSAL object handle, and initializes a global fd for regular files. `deconstruct_handle` verifies the export id from the op context, releases the Ceph inode with `ceph_ll_put`, destroys regular-file fd state, finalizes the FSAL handle, and frees memory. Attribute conversion helpers set FSAL valid masks only for statx fields present. ACL helpers read POSIX ACL xattrs, convert them to NFSv4 ACLs, and write FSAL ACLs back to POSIX xattr format.

## State and Persistence Behavior

The file creates and destroys in-memory object handles and owns the shared `ceph_mount` lookup tree state. It persists no files itself, but ACL helpers read and write persistent CephFS ACL xattrs. The AVL key compares filesystem name, mount path, user id, and secret key so exports can share or isolate libcephfs sessions.

## Dependencies and Integration Points

Dependencies include libcephfs inode lifetime APIs, Ganesha FSAL object initialization, POSIX mode/dev conversion, optional `libacl`/POSIX ACL conversion helpers, `nfs_exports.h` options, and the Ceph module/global op context. It is used by `main.c` during export root creation, `export.c` during filehandle reconstruction, and `handle.c` for every object returned to upper layers.

## Risks and Edge Cases

`deconstruct_handle` relies on the active `op_ctx->fsal_export` matching the object export id; calling it under the wrong context would release the inode through the wrong mount. ACL conversion can allocate zero ACEs or produce malformed ACLs if xattr data is corrupt. `ceph_mount_key_cmpf` treats `NULL` and non-`NULL` keys distinctly and asserts `cm_mount_path`, so create paths must always populate mount path before AVL operations. Attribute conversion marks sec-label support off when export options disable it, so tests need both option states.

## Test Signals

Useful tests include handle lifecycle with regular and non-regular files, inode ref release under duplicate handle merge/release, attribute masks with partial statx data, creation/change time propagation, ACL get/set on files and directories, corrupt or missing ACL xattrs, mount sharing across identical keys, mount separation across user/secret/filesystem/path changes, AVL insert/remove order, and wrong-export release assertions in debug builds.
