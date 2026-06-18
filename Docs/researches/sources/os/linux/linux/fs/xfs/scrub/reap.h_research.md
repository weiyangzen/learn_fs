# File Research: sources/os/linux/linux/fs/xfs/scrub/reap.h

## Role
Declares block and fork reaping interfaces for online repair.

## Reap API
- `xrep_reap_agblocks` disposes per-AG extents from an AG bitmap.
- `xrep_reap_fsblocks` disposes filesystem block extents from an fsblock bitmap.
- `xrep_reap_ifork` removes all mappings from a scrub target or tempfile fork.
- `xrep_reap_metadir_fsblocks` handles old metadir metadata blocks.
- `xrep_reap_rtblocks` handles realtime extents when realtime support is enabled, otherwise returns `-EOPNOTSUPP`.

## Buffer Scan API
- `struct xrep_bufscan` tracks daddr, maximum scan length, step size, and internal sector count.
- `xrep_bufscan_max_sectors` computes a bounded scan range.
- `xrep_bufscan_advance` returns matching incore buffers during reap invalidation.
