# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_disk_open.c

## Summary
Provides helpers to open a disk device through a temporary vnode and query its size or wedge/partition identity.

## Main Responsibilities
- Maps a disk `device_t` to its block major and raw-partition `dev_t`.
- Opens a temporary block-device vnode for read-only disk inspection.
- Retrieves disk size with wedge information preferred over disklabel partition info.
- Builds `dkwedge_info` from either native wedge ioctl or partition info fallback.

## Important Behavior
`opendisk()` ignores expected open failures for missing devices, missing media, and busy devices, but logs unexpected errors. It treats `dk` wedge devices differently by using the unit directly rather than `MAKEDISKDEV(..., RAW_PART)`.

`getdisksize()` prefers `DIOCGWEDGEINFO` so large wedge sizes are not constrained by disklabel limits. It validates sector size as nonzero, power of two, not above `MAXBSIZE`, and requires nonzero sector count.

## Dependencies
Uses devsw name-to-block-major conversion, specfs `bdevvp()`, `VOP_OPEN()`, disk and wedge ioctls, `disk_find()`, and partition type naming.

## Risks
Temporary vnode opening depends on the block devsw and driver open path being usable during probing. Fallback disklabel sizes may be too small for large media, which is why wedges are queried first.
