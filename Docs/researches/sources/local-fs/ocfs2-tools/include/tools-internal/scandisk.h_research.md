# File Research: sources/local-fs/ocfs2-tools/include/tools-internal/scandisk.h

## Purpose

Declares internal block-device scanning data structures and scan/free APIs.

## Main Contents

- Default paths for `/dev`, `/sys`, `/sys/block`, and device cache timeout.
- `struct sysfsattrs` records whether sysfs exists for a device and whether it has slaves, holders, is removable, or is a disk.
- `struct devpath` stores linked `/dev` paths for a major/minor device.
- `struct devnode` represents one block device major/minor with paths, sysfs/proc state, proc name, RAID/device-mapper/powerpath flags, and caller filter storage.
- `struct devlisthead` stores list head/tail, cache timestamp/timeout, and scan-source status flags for sysfs, proc partitions, `/dev`, mdstat, mapper, and powerpath detection.
- `devfilter` callback type and `scan_for_dev()` / `free_dev_list()` declarations.

## Dependencies and Integration

- Intended for utilities that enumerate mounted or candidate OCFS2 devices.
- Uses `MAXPATHLEN` and `time_t`, so including sources must provide relevant system headers.

## Research Notes

- Comments define a convention for scan result fields: positive for hit/success, zero for no hit, negative for error.
