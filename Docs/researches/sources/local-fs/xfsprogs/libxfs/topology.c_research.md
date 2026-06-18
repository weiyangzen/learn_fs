# File Research: sources/local-fs/xfsprogs/libxfs/topology.c

## Role

`topology.c` provides mkfs/libxfs device probing and default geometry selection. It calculates default data allocation-group and realtime-group sizes, detects preexisting signatures before overwrite, and gathers logical/physical sector, stripe, and atomic-write topology for data, realtime, and log devices.

## Major Responsibilities

- Calculate default AG size/count with `calc_default_ag_geometry`.
- Calculate default realtime group size/count with `calc_default_rtgroup_geometry`.
- Probe a target path with blkid to detect existing filesystems or partition tables in `check_overwrite`.
- Read blkid topology fields for block devices: logical sector size, physical sector size, minimum I/O size, optimal I/O size, and alignment offset.
- Reject misaligned block devices unless forced.
- Read Linux `statx` atomic write unit bounds when available.
- Handle regular-file targets by deriving direct-I/O sector requirements with `platform_findsizes`.
- Populate `struct fs_topology` for data, realtime, and log subvolumes.

## Geometry Heuristics

`calc_default_ag_geometry` uses size thresholds and storage parallelism to choose a target AG size. Filesystems at or above 32 TiB use the maximum AG size. Single-device filesystems at or above 4 TiB also use the maximum; single-device filesystems from 128 MiB to 4 TiB target four AGs. Multidisk configurations use a higher AG count, reducing the shift for smaller filesystems. The final AG size rounds up if the filesystem size is not evenly divisible.

`calc_default_rtgroup_geometry` mirrors the single-device portion for realtime devices: 4 TiB or larger uses `XFS_MAX_RGBLOCKS`; 128 MiB to 4 TiB targets four realtime groups; smaller devices round similarly.

## Device Probing

`check_overwrite` opens the device, obtains its size, skips zero-length targets, and runs a full blkid probe with partition probing enabled. It reverses blkid's success convention so callers receive `1` for detected content, `0` for nothing, and `-1` for probe/internal failure. Diagnostics distinguish filesystem signatures, partition tables, and unknown blkid detections.

`blkid_get_topology` converts blkid minimum/optimal I/O values from bytes to 512-byte units, suppresses stripe values equal to physical sector size, and handles nonzero alignment offsets. `get_device_topology` chooses between regular-file sizing and block-device blkid/statx probing, then ensures a physical sector size is present.

## Notable Assumptions

- `libxfs_get_topology` silently skips absent optional subvolumes.
- Stripe unit/width are stored in basic-block counts after blkid probing.
- Misalignment can abort the process directly unless the caller requested force overwrite.
- Atomic write unit fields are optional and remain zero when `statx` support or device reporting is absent.
