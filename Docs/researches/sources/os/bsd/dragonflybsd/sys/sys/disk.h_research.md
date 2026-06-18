# File Research: sources/os/bsd/dragonflybsd/sys/sys/disk.h

Kernel disk object, media information, disklabel policy flags, and disk-management API.

Key responsibilities:
- Defines `struct disk_info` carrying media size or block count, block size, disklabel management flags, optional geometry, trim flag, and serial number.
- Defines disk slice/open policy flags for no labels, one slice, compatibility labels/partition A, raw extensions, quiet MBR handling, device mapper naming, and raw psize fallback.
- Defines `struct disk` with dev_ops pointers, flags, open count, raw and special cdevs, slices, disk_info, disk type, list linkage, cluster DMSG iocom, and destruction refs.
- Declares disk creation/destruction, info/type updates, open count, dump checks/config, enumeration, invalidation/unprobe, async/sync disk messages, bounds checks, and cluster iocom helpers.
- Defines disk message IDs for probe, destroy, slice reprobe, disk reprobe, unprobe, and sync.

Dependencies:
- Kernel/kernel-structures only; includes `diskslice.h`, queue, msgport, and `dmsg.h`.

Notable risks:
- `disk_info` allows either byte size or block count, not both; drivers must populate it consistently.
- Disk object participates in devfs, disklabel, dump, and DMSG cluster export paths.
