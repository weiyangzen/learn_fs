# Research: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_LIZARDFS/mds_handle.c

Purpose: Implements LizardFS pNFS MDS object-handle layout operations: LAYOUTGET, LAYOUTRETURN, and LAYOUTCOMMIT.

Important APIs and types: The main functions are `lzfs_fsal_layoutget()`, `lzfs_fsal_layoutreturn()`, `lzfs_fsal_layoutcommit()`, and `lzfs_fsal_handle_ops_pnfs()`. It uses `struct lzfs_fsal_ds_wire` for DS wire handles, `struct pnfs_deviceid`, `FSAL_encode_file_layout()`, and `MFSCHUNKSIZE` as layout stripe unit.

Control flow: `layoutget` validates FILE layout type, fills a device id with FSAL id, export id in `device_id2`, and file inode in `devid`, encodes a DS wire handle containing the inode, and emits a whole-file FILE layout with `return_on_close` and `last_segment` set. `layoutreturn` accepts only FILE layout type and otherwise does no state cleanup. `layoutcommit` validates type, gets current file attributes, optionally grows size to `last_write + 1`, optionally updates mtime if the supplied time is newer, calls `liz_cred_setattr()`, and marks commit done.

State and persistence: Layout grants do not create local reservations. Layout commit can persist size and mtime to LizardFS. DS wire state is just inode.

Dependencies and integration: Depends on pNFS utilities, `op_ctx`, LizardFS wrappers, and handle/export internals. `lzfs_fsal_handle_ops_pnfs()` is called by handle ops initialization when export pNFS MDS is enabled.

Risks: `layoutcommit` sets `attr.st_mtim.tv_sec = arg->new_time.nseconds` instead of assigning `tv_nsec`, corrupting mtime when nanoseconds are supplied. It does not inspect or decode layoutcommit type-specific data beyond generic args. Layoutget logs `res->segment` before setting offset/length locally, relying on caller-provided segment contents. DS wire inode is 32-bit.

Test signals: LAYOUTGET/COMMIT with size growth, mtime-only commit, nanosecond mtime validation, bad layout type, client close return-on-close behavior, DS handle reconstruction from layout, and pNFS writes that extend files through the DS path.
