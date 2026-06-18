# sources/user-network-fs/nfs-ganesha/src/include/pnfs_utils.h

## Purpose
This header provides shared pNFS utility logic for layout range math, XDR encoding of layouts/devices, data-server registry management, and POSIX-to-NFSv4 error conversion.

## Important APIs, Types, And Control Flow
Inline helpers `pnfs_segments_overlap`, `pnfs_segment_contains`, and `pnfs_segment_difference` compare `struct pnfs_segment` ranges while respecting compatible `io_mode` bits and `NFS4_UINT64_MAX` infinite-length segments. Exported encoding APIs include `xdr_fsal_deviceid`, `FSAL_encode_ipv4_netaddr`, `FSAL_encode_file_layout`, `FSAL_encode_v4_multipath`, `FSAL_encode_flex_file_layout`, and `FSAL_encode_ff_device_versions4`. It defines `fsal_multipath_member_t` and declares pNFS data-server lifecycle functions such as `pnfs_ds_alloc`, `pnfs_ds_insert`, `pnfs_ds_get`, `pnfs_ds_put`, `pnfs_ds_remove`, `ReadDataServers`, `remove_all_dss`, and `server_pkginit`.

## State And Persistence
The range helpers are stateless. Data-server functions manage process-global pNFS DS registry state and reference counts; `pnfs_ds_get_ref` increments `ds_refcount` atomically. Persistence is indirect through runtime configuration loaded by `ReadDataServers`, not file writes in this header.

## Dependencies And Integration Points
It depends on `nfs4.h`, `fsal_pnfs.h`, `fsal_api.h`, and `config.h`. It connects FSAL pNFS implementations to NFSv4.1/4.2 layout XDR encoding, data-server discovery, and common error translation.

## Risks And Test Signals
The documented `pnfs_segment_difference` limitation cannot split a middle subtraction, so callers must not assume full interval algebra. Boundary tests are needed for zero-length segments, adjacent ranges, infinite lengths, overflow-prone `offset + length`, mode incompatibility, layout encoding XDR byte streams, DS registry reference balancing, and config parsing failures.
