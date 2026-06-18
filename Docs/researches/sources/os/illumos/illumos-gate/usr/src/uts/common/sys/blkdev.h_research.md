# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/blkdev.h

`blkdev.h` defines the common framework interface for simple block-device drivers that need labeling support without full SCSA complexity. It models fixed queue depth, simple linear non-rotating semantics, limited removable-media support, and no cancellation or request priorities.

Key structs are `bd_xfer` for transfer requests, `bd_drive` for drive identity and free-space constraints, `bd_media` for media geometry/state, `bd_ops` for adapter callbacks, and `bd_errstats` for kstats. The current ops version is `BD_OPS_VERSION_2`, adding free-space behavior. Exported functions allocate/free handles, attach/detach handles, report transfer completion/errors, initialize/finalize module state, and notify state changes.
