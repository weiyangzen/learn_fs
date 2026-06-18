# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_GLUSTER/main.c

Purpose: this file is the module entry point for the Gluster FSAL. It declares the global `GlusterFS` module object, static filesystem capabilities, module-level config parsing for pNFS roles, and load/unload hooks that register and unregister the FSAL with NFS-Ganesha.

Important APIs and functions: `GlusterFS` embeds `fsal_staticfsinfo_t` values such as max name/path length, ACL support, link/symlink/lock support, named attributes, unique handles, pNFS defaults, delegation support, and readdir-plus support. `glfs_params` and `glfs_param` define the global `GLUSTER` config block with `pnfs_mds` and `pnfs_ds`. `init_config()` loads optional config into `GlusterFS.fsal.fs_info` and displays final FS info. `glusterfs_init()` registers the FSAL name `GLUSTER`, installs module operations, initializes pNFS DS operation factories, initializes object ops through `handle_ops_init()`, and initializes the volume list/mutex. `glusterfs_unload()` unregisters the FSAL and validates that no active shares remain.

Control flow: at module load, Ganesha calls `MODULE_INIT`. Registration must succeed before any operation pointers are useful. The file then wires `create_export`, `init_config`, `getdeviceinfo`, and pNFS DS ops into the public module operations. The object operation vector is initialized once globally. At unload, unregister must succeed, the shared filesystem list should be empty, and the mutex is destroyed.

State and persistence: the global module object is process-lifetime state. It holds the shared FS info and all Gluster FS object list state initialized here. The file does not persist to disk; it establishes capability flags that affect every export and operation.

Dependencies and integration: this file depends on FSAL registration APIs, `gluster_internal.h`, commonlib helpers, pNFS hooks from `mds.c`, DS ops from other Gluster FSAL files, and object operations from `handle.c`. Export creation is delegated to `glusterfs_create_export()`.

Risks and test signals: capability flags must match actual operation support. Advertising delegations, pNFS DS, named attrs, ACLs, or readdir-plus incorrectly can expose unsupported paths to clients. The config block is optional and treats parse failures as harmless unless non-harmless errors are reported. Tests should include module load/unload, global config parse with pNFS booleans, export creation after init, pNFS feature negotiation, and unload with active exports to confirm warnings rather than crashes.
