# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/fs/smbsrv/smb_nt_transact_ioctl.c

## Summary
Implements SMB1 NT transact FSCTL/IOCTL dispatch for a small supported set of Windows filesystem control codes.

## Main Responsibilities
- Decodes function code, FID, FSCTL flag, and command flags.
- Dispatches recognized FSCTLs through a static table.
- Implements sparse attribute toggling.
- Validates but does not implement zero-data punching.
- Returns simple allocated-range information.
- Delegates snapshot enumeration to VSS support.
- Rejects or no-ops selected FSCTLs for compatibility.

## Key APIs
- `smb_nt_transact_ioctl()`.
- `smb_nt_trans_ioctl_set_sparse()`.
- `smb_nt_trans_ioctl_set_zero_data()`.
- `smb_nt_trans_ioctl_query_alloc_ranges()`.
- `smb_nt_trans_ioctl_enum_snaps()`.

## Important Behavior
Unsupported function codes return `NT_STATUS_NOT_SUPPORTED`. `FSCTL_GET_OBJECT_ID` returns invalid parameter, and `FSCTL_FIND_FILES_BY_SID` succeeds as a no-op.

`SET_SPARSE` requires writable tree, non-IPC disk file, non-directory handle, then reads and updates DOS attributes through `smb_node_getattr()` and `smb_node_setattr()`.

`QUERY_ALLOCATED_RANGES` returns no data for zero-length files. Otherwise it decodes the requested offset/length and returns exactly that single range, regardless of real sparse extents.

`SRV_ENUMERATE_SNAPSHOTS` validates the handle and calls `smb_vss_enum_snapshots()` with response data in `xa->rep_data_mb`.

## Dependencies
Relies on ofile lookup/release, node attribute helpers, DOS sparse attribute support, VSS snapshot enumeration, SMB FSCTL constants, and mbuf-chain encoding.

## Risks
`FSCTL_SET_ZERO_DATA` is explicitly marked as a no-op bug and does not punch or zero file ranges. The comment notes that proper support must break oplocks.

`QUERY_ALLOCATED_RANGES` is a compatibility approximation, not an accurate sparse extent query.
