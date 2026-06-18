# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_getdevicelist.c

Purpose: implements pNFS `GETDEVICELIST`, returning device ids for a filesystem/layout type.

Important APIs and types: uses `GETDEVICELIST4args`, `GETDEVICELIST4res`, `GETDEVICELIST4resok`, `struct fsal_getdevicelist_res`, and a local `cb_data` callback carrier. It calls `nfs4_sanity_check_FH`, `op_ctx->fsal_export->exp_ops.getdevicelist`, `check_resp_room`, and `gsh_malloc/free`.

Control flow: minorversion 0 is rejected, then the current filehandle is checked. The handler initializes FSAL cookie and verifier from request arguments. It allocates a fixed array for up to 32 device ids and passes a callback to the FSAL. The callback writes a device id composed from the current export id (`swexport`) and the FSAL-provided id in network order, incrementing the count. After the FSAL returns, the handler sizes the response, checks response room, copies output cookie/verifier/eof, and records the returned list length.

State and persistence: read-only with respect to state. It allocates a device list result buffer freed by `nfs4_op_getdevicelist_Free` only on success; FSAL failure and response-room failure free the buffer in-line.

Dependencies and integration: depends on current export in `op_ctx`, FSAL pNFS `getdevicelist`, NFSv4 verifier/cookie conventions, pNFS device id packing, and response sizing.

Risks: the callback checks `count > max`, not `count >= max`, so a full list can write at index `max`; this is a boundary risk around the fixed 32-entry allocation. The handler ignores client-provided `gdla_maxdevices` style bounds if the protocol has one and uses its local max. Device id byte casting assumes alignment and deviceid layout.

Test signals: minorversion 0, invalid current FH, FSAL returns zero devices, exactly 32 and more than 32 devices, non-zero cookies/verifiers, response-room failure, and successful free of result list.
