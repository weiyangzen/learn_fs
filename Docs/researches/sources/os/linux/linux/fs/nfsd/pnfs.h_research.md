# File Research: sources/os/linux/linux/fs/nfsd/pnfs.h

## Summary
Declares the NFSD pNFS server-side layout interface and compile-time stubs. It connects NFSv4.1+ layout operations to concrete block, SCSI, and flexfile layout implementations when configured.

## Main Responsibilities
- Defines the pNFS device-id map and layout operation vector.
- Declares layout driver hooks for GETDEVICEINFO, LAYOUTGET, LAYOUTCOMMIT, layout encoding, client fencing, and recall behavior.
- Exposes common pNFS stateid preprocessing, layout insertion, layout return, device-id generation, and device-id lookup helpers.
- Provides initialization, teardown, layout-type setup, client/file layout return, and layout close APIs.
- Supplies no-op stubs when `CONFIG_NFSD_PNFS` or `CONFIG_NFSD_V4` support is absent.

## Key Data Structures and Interfaces
- `struct nfsd4_deviceid_map` maps an index and fsid data to generated pNFS device IDs.
- `struct nfsd4_layout_ops` is the per-layout-type method table.
- `nfsd4_layout_ops[]` indexes available layout drivers.
- Optional externs expose `bl_layout_ops`, `scsi_layout_ops`, and `ff_layout_ops`.

## Important Behavior
The interface separates protocol preprocessing from filesystem/layout-specific encoding and commit behavior. Layout implementations can disable recalls, advertise notification types, and provide a fencing callback for client isolation.

`MAX_FENCE_DELAY` caps exponential backoff for fence retries at three minutes.

## Dependencies
Depends on NFSv4 NFSD state structures, exportfs, NFS export definitions, NFSv4 XDR declarations, and optional block/SCSI/flexfile layout configuration.

## Risks and Subtleties
The header deliberately compiles away pNFS behavior when unsupported. Callers must not assume layout state exists unless the relevant config is enabled, and layout driver hooks must honor shared stateid and recall rules from `state.h`.
