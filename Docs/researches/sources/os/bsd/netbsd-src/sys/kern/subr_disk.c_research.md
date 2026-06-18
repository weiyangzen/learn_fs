# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_disk.c

## Summary
Implements common disk support: error formatting, disk lifecycle, I/O statistics, bounds checks, disklabel conversion, disk ioctls, and disk geometry/property publication.

## Main Responsibilities
- Formats transfer errors with partition, block range, and optional CHS detail.
- Finds disks through iostat names.
- Initializes, attaches, detaches, destroys, renames, and begin-detaches `struct disk`.
- Maintains disk I/O statistics through iostat helpers.
- Bounds-checks raw media and labeled partition transfers.
- Reads sectors through a driver strategy routine.
- Converts legacy labels to ensure a usable raw partition exists.
- Handles generic disk ioctls for disk info, geometry, partition info, wedges, sector alignment, and labels.
- Canonicalizes disk geometry and exports `disk-info` property dictionaries.

## Important Behavior
`bounds_check_with_label()` rejects negative offsets, protects the on-disk label from writes unless `wlabel` is set, truncates transfers at partition end, reports EOF at exact end, and computes `b_cylinder` for queue sorting.

`disk_ioctl()` passes unknown commands through with `EPASSTHROUGH`, enforces write permission for wedge mutating operations, and returns raw partition size from disk geometry rather than disklabel partitions.

`disk_set_info()` fills missing sector size and derived sector count/cylinder fields, stores geometry in a proplib dictionary, and mirrors it into the device properties when a device is supplied.

## Dependencies
Uses `struct disk`, `disklabel`, `buf`, iostat, wedge management, proplib, disk ioctls, and kernel logging.

## Risks
Label and geometry paths retain compatibility behavior for old disklabel assumptions. Some partition block-size logic is explicitly called out as buffer-cache legacy behavior and mainly reliable for BSD FFS metadata.
