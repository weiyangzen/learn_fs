# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/nfs/nfs4x_xdr.c

## Purpose

This file provides hand-maintained XDR encode/decode/free routines for NFSv4 minor-version extensions, mainly NFSv4.1 and NFSv4.2 protocol data. It is explicitly not a raw `rpcgen` output file: the header warns that generated code must be manually integrated because this file contains hand-coded attribute XDR.

## Main Responsibilities

- Encode/decode NFSv4.1 scalar and compound data types:
  - `verifier4`, `sequenceid4`, `sessionid4`, `slotid4`, `clientid4`, `stateid4`, `offset4`, `length4`, `count4`, `mode4`.
- Encode/decode NFSv4.1 attributes and metadata:
  - ACL flags and `nfsacl41`.
  - mode-set-masked attributes.
  - implementation identity, fs status, charset capability, retention attributes, fs locations info.
- Encode/decode pNFS structures:
  - layout type/content/iomode.
  - device IDs and device addresses.
  - layout get/commit/return/update.
  - file-layout data-server address and file-layout bodies.
  - layout recall callback structures.
- Encode/decode NFSv4.1 session and backchannel operations:
  - `BACKCHANNEL_CTL`, `BIND_CONN_TO_SESSION`, `EXCHANGE_ID`, `CREATE_SESSION`, `DESTROY_SESSION`, `SEQUENCE`, `SET_SSV`, `TEST_STATEID`, `FREE_STATEID`, `RECLAIM_COMPLETE`.
- Encode/decode NFSv4.2 operations:
  - `ALLOCATE`, `COPY`, `COPY_NOTIFY`, `DEALLOCATE`, `IO_ADVISE`, `LAYOUTERROR`, `LAYOUTSTATS`, `OFFLOAD_CANCEL`, `OFFLOAD_STATUS`, `READ_PLUS`, `SEEK`, `WRITE_SAME`, `CLONE`.
- Encode/decode NFSv4.1 callback operations:
  - layout recall, notify, push delegation, recall any, recallable object available, recall slot, callback sequence, wants cancelled, notify lock, notify device ID.
- Dispatch operation-specific unions via:
  - `xdr_nfs4x_argop4()`.
  - `xdr_nfs4x_resop4()`.
  - `xdr_nfs_cb_argop4()`.
  - `xdr_nfs_cb_resop4()`.

## Important Control Flow

Most functions are thin XDR wrappers that serialize fields in wire order and return `FALSE` on the first failed field. Union-like protocol structures are handled by reading or using an enum/status discriminator, then switching to the correct arm.

Key dispatchers:

- `xdr_nfs4x_argop4()` assumes the operation number was already XDR’d and switches on `objp->argop` for all NFSv4.1 and NFSv4.2 argument bodies.
- `xdr_nfs4x_resop4()` mirrors argument dispatch for result bodies, including status-dependent success payloads.
- `xdr_nfs_cb_argop4()` dispatches callback argument bodies for NFSv4.1 callback operations.
- `xdr_nfs_cb_resop4()` reads `resop` itself with `xdr_u_int()` and dispatches callback result bodies, including legacy callback results such as `OP_CB_GETATTR`, `OP_CB_RECALL`, and `OP_CB_ILLEGAL`.

Status-dependent result routines generally encode a status first and only encode success payloads on `NFS4_OK`; some operations encode specific failure payloads, such as:

- `GETDEVICEINFO` encodes `gdir_mincount` on `NFS4ERR_TOOSMALL`.
- `LAYOUTGET` encodes `logr_will_signal_layout_avail` on `NFS4ERR_LAYOUTTRYLATER`.
- `COPY` encodes copy requirements on `NFS4ERR_OFFLOAD_NO_REQS`.

## Notable Implementation Details

- `xdr_bitmap4_notify()` is a special single-word bitmap encoder used for notification bitmaps. It asserts encode mode and writes a length of `1`, then selects the correct 32-bit word depending on endian layout.
- `xdr_layoutrecall_file()` decodes and frees file handles but deliberately returns `FALSE` for encode with a `TODO: encode nfs4x_fh` comment.
- Several optional protocol fields are modeled as XDR arrays with max length `1`, such as optional retention begin time, optional stateids, and optional cookies.
- Opaque values use bounded XDR helpers where protocol limits exist, for example `NFS4_OPAQUE_LIMIT`, `NFS4_SESSIONID_SIZE`, `NFS4_DEVICEID4_SIZE`, and `NFS4_FHSIZE`.
- `xdr_netloc4()` rejects unknown netloc union discriminants instead of ignoring them.

## Dependencies

- Includes:
  - `<sys/statvfs.h>`
  - `<sys/sysmacros.h>`
  - `<sys/sdt.h>`
  - `<nfs/nfs4.h>`
  - `<nfs/nfs4_attr.h>`
- Reuses common NFSv4 XDR helpers from elsewhere, including:
  - `xdr_fattr4`
  - `xdr_nfsace4`
  - `xdr_bitmap4`
  - `xdr_nfstime4`
  - `xdr_utf8string`
  - `xdr_nfs_fh4`
  - `xdr_SECINFO4res`

## State and Memory Ownership

This file does not maintain persistent state. Memory ownership is delegated to XDR array/string/bytes routines. Routines that process variable-length arrays pass field pointers and length pointers into `xdr_array()` or `xdr_bytes()`, so decode/free behavior depends on the standard XDR memory semantics.

## Risks and Edge Cases

- Unknown enum discriminants generally return `FALSE`, which is strict and appropriate for protocol XDR but can reject forward-compatible values.
- `xdr_layoutrecall_file()` cannot encode file-layout recall file handles yet, so any path needing that encode direction will fail.
- Notification bitmaps rely on endian-specific layout assumptions in `xdr_bitmap4_notify()`.
- Many arrays use `~0` as max length, relying on upstream request sizing and XDR allocation behavior rather than local semantic caps.
- This file must stay synchronized with NFSv4 protocol structs in headers; hand-maintained XDR makes drift a real integration risk.

## Testing Notes

Useful tests would exercise encode/decode/free round trips for:

- Session setup operations.
- pNFS layout/device operations.
- NFSv4.2 sparse/offload operations.
- Callback sequence and notification operations.
- Error-result arms with non-success payloads.
- Little-endian and big-endian bitmap notification encoding.
