# Research: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_KVSFS/kvsfs_xattrs.c

Purpose: Provides the KVSFS extended-attribute operation symbols required by the object ops vector, but the implementation is effectively a placeholder.

Important APIs and types: The file defines local callback typedefs `xattr_getfunc_t` and `xattr_setfunc_t`, an unused `fsal_xattr_def_t`, a diagnostic `print_vfshandle()`, and all FSAL xattr entry points declared in `kvsfs_methods.h`: list, name-to-id, get by id/name, set by name/id, get xattr attrs, and remove by id/name.

Control flow: Every public xattr function returns `ERR_FSAL_NO_ERROR` immediately without filling output buffers, ids, counts, attributes, or end-of-list markers. `print_vfshandle()` writes the fixed text `(not yet implemented)` into a caller buffer, but is not connected to a xattr table.

State and persistence: No xattr state is read or written. No KVSNS xattr API is called. As a result, named attribute operations can appear successful while doing nothing.

Dependencies and integration: Includes Ganesha list/config/commonlib headers, `fsal_convert`, and `kvsfs_fsal_internal.h`. The functions are installed into object ops by `kvsfs_handle_ops_init()`, and `kvsfs_main.c` advertises `named_attr = true`.

Risks: Silent success is the main correctness risk. Clients may believe xattrs were set or removed when no persistence occurred. Output parameters can remain uninitialized, especially `p_nb_returned`, `end_of_list`, `pxattr_id`, `p_output_size`, and `p_attrs`. This conflicts with module capability advertisement and can cause protocol-visible corruption or client hangs.

Test signals: NFSv4 named attribute operations should verify list counts and EOF, set/get/remove round trips, small-buffer behavior, unknown names, and whether unsupported xattrs should return `ERR_FSAL_NOTSUPP` instead of success. Static fsinfo should be reconciled with real support.
