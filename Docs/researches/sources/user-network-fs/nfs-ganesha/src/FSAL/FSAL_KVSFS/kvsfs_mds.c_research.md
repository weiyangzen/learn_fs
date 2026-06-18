# Research: sources/user-network-fs/nfs-ganesha/src/FSAL/FSAL_KVSFS/kvsfs_mds.c

Purpose: Implements the KVSFS pNFS metadata-server side for NFSv4.1 FILE layouts: layout type discovery, device address encoding, layout grant, return, and commit hooks.

Important APIs and types: Public integration functions are `export_ops_pnfs()`, `handle_ops_pnfs()`, `kvsfs_getdeviceinfo()`, and `kvsfs_fs_da_addr_size()`. It uses `struct kvsfs_exp_pnfs_parameter` from `kvsfs_methods.h` for stripe unit, DS count, and fixed DS address array. Layout encoding uses Ganesha helpers `FSAL_encode_v4_multipath()` and `FSAL_encode_file_layout()`.

Control flow: Export pNFS ops advertise only `LAYOUT4_NFSV4_1_FILES`, a 4 MiB block size, one segment, and fixed loc-body/device-address sizes. `kvsfs_getdeviceinfo()` finds the first export on the module export list, reads its pNFS DS array, encodes stripe indices, encodes one multipath member per configured DS, and returns NFSv4 status. `kvsfs_layoutget()` validates layout type, copies the object's KVSFS file handle into a DS handle descriptor, grants a whole-file segment with `return_on_close`, builds device id `1`, and encodes the file layout. `layoutreturn` and `layoutcommit` validate layout type and otherwise mostly acknowledge.

State and persistence: pNFS DS topology is stored in the export's `pnfs_param`; layout grants do not create persistent reservations. The DS wire body embeds a KVSFS file handle. Layout commit currently does not persist size/time changes.

Dependencies and integration: Depends on Ganesha pNFS/XDR helpers, module export list, `op_ctx`, `struct pnfs_deviceid`, and KVSFS handle internals. It is registered from `kvsfs_main.c` and conditionally installed on object ops from `kvsfs_alloc_handle()` when the export is pNFS MDS-enabled.

Risks: `kvsfs_getdeviceinfo()` uses the first export in `fsal_hdl->exports` instead of matching `deviceid`, which is unsafe with multiple exports. `ipport` is stored separately from `sockaddr_in` and is converted with `ntohs()` despite being an `unsigned short`; config byte order must be verified. Layoutcommit is a stub and can hide DS-side size/time updates. The fixed device address buffer size is heuristic. Multiple DS handling is marked TODO in layoutget.

Test signals: Validate GETDEVICEINFO with zero, one, and four DS entries; multi-export pNFS configurations; client LAYOUTGET/RETURN/COMMIT; bad layout type handling; XDR buffer exhaustion; and DS address byte order on the wire.
