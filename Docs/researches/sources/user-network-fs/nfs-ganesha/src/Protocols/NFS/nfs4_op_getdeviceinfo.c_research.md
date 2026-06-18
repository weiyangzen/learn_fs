# sources/user-network-fs/nfs-ganesha/src/Protocols/NFS/nfs4_op_getdeviceinfo.c

Purpose: implements pNFS `GETDEVICEINFO`, returning FSAL-encoded device address information for a supplied device id and layout type.

Important APIs and types: uses `GETDEVICEINFO4args`, `GETDEVICEINFO4res`, `GETDEVICEINFO4resok`, `struct pnfs_deviceid`, `struct fsal_module`, and XDR streams. It uses the global `pnfs_fsal` table, `fs_da_addr_size`, `getdeviceinfo`, `xdrmem_create`, and `check_resp_room`.

Control flow: minorversion 0 is rejected. The handler overlays Ganesha's `pnfs_deviceid` on the wire `deviceid4` bytes, validates `fsal_id`, and looks up the FSAL module. It computes a minimum response count, asks the FSAL for maximum device address body size, and caps allocation by the client's `gdia_maxcount`. The FSAL encodes the `da_addr_body` into an in-memory XDR stream. After encoding, the handler checks response room, clears the notification bitmap, and attaches the allocated buffer to the result. Any error frees the allocated buffer before setting `gdir_status`.

State and persistence: read-only with respect to NFS state. It allocates an opaque response buffer owned by the XDR result until `nfs4_op_getdeviceinfo_Free`.

Dependencies and integration: integrated with pNFS FSAL module registration, FSAL layout-specific device encoding, compound response sizing, and export/device id conventions.

Risks: `gdia_maxcount` smaller than the base response can underflow when computing `gdia_maxcount - mincount`; callers rely on unsigned/count behavior and FSAL size checks. Invalid or inactive FSAL ids must not index beyond `pnfs_fsal`. FSALs must report non-zero address sizes and must not overrun the XDR stream.

Test signals: minorversion 0, invalid fsal id, inactive FSAL, tiny `maxcount`, FSAL getdeviceinfo failure, response-room failure, successful opaque body encoding, and cleanup of successful/error buffers.
