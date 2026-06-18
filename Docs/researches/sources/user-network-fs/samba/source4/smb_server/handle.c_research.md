# Research: sources/user-network-fs/samba/source4/smb_server/handle.c

Purpose: manages per-tree-connect SMB handle IDs and their lifetime.

Important APIs: `smbsrv_init_handles()` initializes an idtree with a masked 24-bit limit and an empty list. The private `smbsrv_handle_find()` validates nonzero ID, limit, idtree lookup, type, and `ntvfs` validity before updating `last_use_time`. `smbsrv_smb_handle_find()` and `smbsrv_smb2_handle_find()` adapt SMB1 `fnum` and SMB2 handle IDs. `smbsrv_handle_new()` allocates a handle, reserves an ID with `idr_get_new_above()`, links it to the tcon list and session handle list, installs a destructor, and records open/last-use times.

State and persistence: state is in `tcon->handles.idtree_hid`, `tcon->handles.list`, and `session->handles`. The destructor removes all links and frees the NTVFS backend handle.

Dependencies and integration: depends on talloc destructors, idtree allocation, DLIST macros, and NTVFS handle ownership. Request handlers use these helpers to validate client-provided handle IDs.

Risks and test signals: ID exhaustion returns NULL after logging. A handle is hidden until `handle->ntvfs` is set, which prevents premature use but requires backend setup ordering. Signals come from open/close, file ID, and handle lifetime torture tests.
