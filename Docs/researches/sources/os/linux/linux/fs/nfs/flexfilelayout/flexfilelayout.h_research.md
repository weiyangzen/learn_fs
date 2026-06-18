# File Research: sources/os/linux/linux/fs/nfs/flexfilelayout/flexfilelayout.h

## Purpose
Defines the core data structures, constants, inline helpers, and cross-file function declarations for the NFSv4 flexfile layout driver.

## Key Definitions
- Layout flags:
  - `FF_FLAGS_NO_LAYOUTCOMMIT`
  - `FF_FLAGS_NO_IO_THRU_MDS`
  - `FF_FLAGS_NO_READ_IO`
- Safety limits:
  - `NFS4_FLEXFILE_LAYOUT_MAX_MIRROR_CNT`
  - `NFS4_FLEXFILE_LAYOUT_MAX_STRIPE_CNT`
- Layoutstats limits:
  - `FF_LAYOUTSTATS_REPORT_INTERVAL`
  - `FF_LAYOUTSTATS_MAXDEV`

## Core Structures
- `struct nfs4_ff_ds_version`: DS NFS version/minor version, rsize/wsize, coupling mode.
- `struct nfs4_ff_layout_ds`: deviceid node plus DS version table and `nfs4_pnfs_ds`.
- `struct nfs4_ff_layout_ds_err`: layout DS error record for layoutreturn/layouterror.
- `struct nfs4_ff_io_stat`, `struct nfs4_ff_busy_timer`, `struct nfs4_ff_layoutstat`: per-DSS layoutstats accounting.
- `struct nfs4_ff_layout_ds_stripe`: one data-server stripe, including device ID, filehandle versions, stateid, DS credentials, localio state, stats, and resolved DS pointer.
- `struct nfs4_ff_layout_mirror`: mirror containing DSS stripes, refcount, stats lock, flags, and report interval.
- `struct nfs4_ff_layout_segment`: pNFS layout segment with stripe unit, flags, and flexible mirror array.
- `struct nfs4_flexfile_layout`: per-inode layout header with commit info, mirror registry, DS error list, and last stats report time.
- `struct nfs4_flexfile_layoutreturn_args`: private layoutreturn payload state.

## Helper Semantics
- Container helpers convert generic pNFS structures into flexfile-specific structures.
- `FF_LAYOUT_COMP()` safely indexes a mirror by layout segment and mirror index.
- `FF_LAYOUT_DEVID_NODE()` resolves a DSS deviceid node if the DS is available.
- `ff_layout_no_fallback_to_mds()` and `ff_layout_no_read_on_rw()` interpret server layout flags.
- `nfs4_ff_layout_calc_dss_id()` maps an offset to a stripe index using stripe unit and DSS count.

## Cross-File API
Declares the flexfile deviceid and error helpers implemented in `flexfilelayoutdev.c`, plus DS selection/client/credential helpers consumed by `flexfilelayout.c`.

## Research Notes
This header is the contract between the flexfile layout core and device/error support code. The flexible array and refcounted mirror structures are especially important for memory layout and lifetime correctness.
