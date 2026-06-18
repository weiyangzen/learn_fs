# Research: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_KVSFS/kvsfs_main.c

Purpose: Defines the KVSFS FSAL module object, static filesystem capabilities, module load/unload hooks, and module-level configuration initialization.

Important APIs and types: The global `struct kvsfs_fsal_module KVSFS` embeds `struct fsal_module` and the shared object operation vector. Its `fs_info` advertises large files, POSIX name/path limits, hard-link support, no symlink support in static info, named attributes, unique handles, supported attribute mask, max I/O size, and no lock support. `kvsfs_init_config()` is the module config callback. `kvsfs_load()` and `kvsfs_unload()` are the `MODULE_INIT` and `MODULE_FINI` entry points.

Control flow: On load, `kvsfs_load()` registers the FSAL under name `KVSFS` with `FSAL_ID_KVSFS`, installs module callbacks for export creation and config initialization, installs pNFS module callbacks (`kvsfs_pnfs_ds_ops_init`, `kvsfs_getdeviceinfo`, `kvsfs_fs_da_addr_size`), and initializes handle ops with `kvsfs_handle_ops_init()`. On unload, it unregisters the FSAL. `kvsfs_init_config()` currently logs static fsinfo and supported attributes without parsing tunables.

State and persistence: The only state is the global module object and its initialized ops vectors. Persistent filesystem state belongs to KVSNS and per-export objects created elsewhere.

Dependencies and integration: Includes Ganesha FSAL init/API headers, pNFS utilities, and KVSFS internal/method headers. The module depends on `kvsfs_create_export()` being provided by the export implementation and on pNFS helpers from KVSFS MDS/DS code.

Risks: Static capability flags are policy-sensitive; this file says `symlink_support = false` while handle code implements symlink creation/read, so client behavior may not match implementation. `named_attr = true` is marked with `XXX` while xattr functions are stubs. `lock_support = false` despite a lock-op prototype elsewhere should be verified. Failed registration only prints to stderr.

Test signals: Load/unload module under Ganesha, verify advertised FSAL capabilities through config dump and NFS client behavior, check pNFS callback registration when KVSFS pNFS is enabled, and confirm unsupported features are not advertised inconsistently.
