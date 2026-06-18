# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/reap.h

This header declares block reaping APIs used by online repair.

APIs:
- `xrep_reap_agblocks`: dispose of AG-block bitmap extents for a given owner/reservation type.
- `xrep_reap_fsblocks`: dispose of fsblock bitmap extents.
- `xrep_reap_ifork`: reap all mappings from an inode fork.
- `xrep_reap_metadir_fsblocks`: reap old metadata directory file btree blocks.
- `xrep_reap_rtblocks`: realtime block reaping when realtime support is enabled, otherwise `-EOPNOTSUPP`.

It also defines `struct xrep_bufscan`, a small state machine for scanning incore buffers by disk address and sector length, plus:
- `xrep_bufscan_max_sectors`
- `xrep_bufscan_advance`

The buffer scan helpers are shared by AG extent and inode-fork reaping paths to find stale cached buffers before freeing old metadata blocks.
