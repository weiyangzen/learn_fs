# sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_VFS/subfsal.h

Purpose: this header defines the VFS sub-FSAL extension interface used by plain VFS, Lustre-over-VFS, and related modules.

Important APIs: `vfs_sub_export_param` exposes sub-FSAL export config parameters. `vfs_sub_fini`, `vfs_sub_init_export_ops`, `vfs_sub_init_export`, `vfs_sub_alloc_handle`, and `vfs_sub_init_handle` let each sub-FSAL extend export operations, allocate larger private handles, and attach per-handle operations/data.

Control flow and state: export creation calls sub-FSAL init hooks after base export setup; handle allocation goes through `vfs_sub_alloc_handle` so sub-FSAL-specific structs can embed or extend `vfs_fsal_obj_handle`; handle initialization calls `vfs_sub_init_handle`.

Dependencies and integration points: included by VFS export/handle code and implemented by sub-FSAL-specific files such as `vfs/subfsal_vfs.c` or Lustre variants.

Risks: allocation layout is critical because the returned object must contain a valid `vfs_file_handle_t` area pointed to by `handle`. Hook ordering must match export lifetime or sub-FSAL cleanup can see partially initialized objects.

Test signals: plain VFS and Lustre module initialization, export config parsing, handle allocation size/layout, and cleanup ordering on export creation failure.
