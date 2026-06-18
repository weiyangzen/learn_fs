# File Research: sources/os/linux/linux-stable/fs/nfs/flexfilelayout/flexfilelayoutdev.c

## Purpose

Implements flexfile deviceid decoding, DS connection preparation, DS credential selection, DS error aggregation, and fallback-availability policy.

## Main Entry Points

- `nfs4_ff_alloc_deviceid_node()`: decodes GETDEVICEINFO opaque data into DS addresses and supported protocol versions.
- `nfs4_ff_layout_prepare_ds()`: resolves a mirror stripe’s deviceid, connects to the DS, clamps rsize/wsize to RPC payload limits, and reports connection failures.
- `nfs4_ff_find_or_create_ds_client()`: returns the correct DS RPC client for NFSv3 or NFSv4 DS access.
- `ff_layout_get_ds_cred()`: chooses per-DS credentials unless the DS is tightly coupled.
- `ff_layout_track_ds_error()`: records DS I/O errors for LAYOUTERROR/LAYOUTRETURN.
- `ff_layout_encode_ds_ioerr()` / `ff_layout_fetch_ds_ioerr()` / `ff_layout_free_ds_ioerr()`: serialize, move, cap, and free tracked error records.
- `ff_layout_avoid_mds_available_ds()` / `ff_layout_avoid_read_on_rw()`: expose fallback policy decisions.

## Control Flow And State

Deviceid allocation decodes multipath DS addresses, filters unsupported DS NFS versions, normalizes I/O sizes, and installs an `nfs4_pnfs_ds` address object. DS preparation lazily resolves device IDs into `mirror_ds` with `cmpxchg`, connects if no DS client exists, probes localio, and records `NFS4ERR_NXIO` plus LAYOUTERROR on failure. RW layouts mark for return when any required mirror is unusable; read layouts can continue if any mirror is still usable.

Error tracking stores sorted, mergeable records keyed by opnum, status, stateid, deviceid, and adjacent/overlapping byte ranges. Fetching moves matching records out of the layout list and discards overflow when a caller’s maximum is reached.

## Dependencies

Uses pNFS deviceid helpers, DS address decoding, DS connection helpers, RPC client creation, NFSv4 stateid utilities, inode locking, RCU credentials, and flexfile structures from `flexfilelayout.h`.

## Risks

Deviceid and DS connection state is shared across racing I/O paths, so the lazy `mirror_ds` initialization and deviceid refcounting must remain precise. Error-list merging is order-sensitive and protected by `i_lock`; mistakes can lose LAYOUTRETURN diagnostics or grow unbounded. Read and RW availability differ deliberately: reads require one usable mirror, writes require all mirrors.
