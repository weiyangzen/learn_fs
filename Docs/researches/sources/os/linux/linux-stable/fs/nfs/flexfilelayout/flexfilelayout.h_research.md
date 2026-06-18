# File Research: sources/os/linux/linux-stable/fs/nfs/flexfilelayout/flexfilelayout.h

## Purpose

Defines the private data model and helper API for the NFSv4 flexfile pNFS layout driver.

## API Surface

- Layout flags: `FF_FLAGS_NO_LAYOUTCOMMIT`, `FF_FLAGS_NO_IO_THRU_MDS`, and `FF_FLAGS_NO_READ_IO`.
- Limits and stats constants: maximum mirror/stripe counts and layoutstats intervals.
- `struct nfs4_ff_layout_ds`: cached flexfile deviceid node, supported DS protocol versions, and DS address object.
- `struct nfs4_ff_layout_mirror`: one mirror containing DS stripes, credentials, stats, refcount, lock, and reporting state.
- `struct nfs4_ff_layout_ds_stripe`: per-stripe device ID, filehandles, DS stateid, DS credentials, localio state, and read/write stats.
- `struct nfs4_ff_layout_segment`: pNFS segment plus stripe unit, flags, and mirror array.
- `struct nfs4_flexfile_layout`: per-layout header, commit info, mirror list, error list, and last stats report time.
- Inline helpers convert generic pNFS headers to flexfile objects, compute stripe IDs, expose mirror/deviceid counts, and interpret fallback/read restrictions.
- Function declarations cover deviceid allocation, DS preparation, DS credential/filehandle selection, error tracking/encoding, LAYOUTERROR sending, and fallback policy.

## Dependencies

Includes Linux refcounting and NFS pNFS declarations. It is consumed by both `flexfilelayout.c` and `flexfilelayoutdev.c`.

## Risks

This header is the shared contract between the flexfile I/O path and device/error path. The flexible-array layout segment and per-mirror refcounting require callers to respect lifetime rules. `nfs4_ff_layout_calc_dss_id()` assumes validated stripe counts and stripe unit semantics from layout decoding.
