# File Research: sources/os/linux/linux/fs/afs/protocol_yfs.h

## Scope

This header defines YFS protocol constants and packed XDR wire structures used by the Linux AFS client when talking to YFS-compatible file servers and cache-manager callback services.

## APIs And Constants

- Service IDs: `YFS_FS_SERVICE`, `YFS_CM_SERVICE`, and callback maximum `YFSCBMAX`.
- Callback opcodes in `enum YFS_CM_Operations`, including probe, callback-state, server preference, cell lookup, and `YFSCBCallBack`.
- File-server opcodes in `enum YFS_FS_Operations`, including fetch/store status, data, ACLs, create/remove/rename/link/mkdir/symlink, locks, volume status, and YFS-specific opaque ACL operations.
- XDR conversion helpers: `xdr_to_u64()` and `u64_to_xdr()`.
- Packed XDR records for 64-bit integers, vnode/FID values, fetch/store status, callbacks, RPC flags, VolSync, volume status, and store-volume-status.
- YFS volume type, volume-state flags, file-lock type constants, and viced capability flags.

## Dependencies

- Uses Linux byte-order helpers `ntohl()` and `htonl()` and big-endian `__be32` wire fields.
- Consumed by YFS client RPC encoders/decoders and callback service handling.

## Risks And Invariants

- Every structure is `__packed` because it mirrors network XDR layout.
- 64-bit values are transferred as two 32-bit words; conversion helpers must be used consistently.
- Negative lock constants such as `yfs_LockNone = -1` are protocol values, not ordinary unsigned flags.
