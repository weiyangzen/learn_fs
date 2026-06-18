# File Research: sources/os/bsd/dragonflybsd/sys/sys/diskslice.h

Disk slice/partition management ABI and kernel helpers for minor encoding, open masks, probing, and partition info.

Key responsibilities:
- Defines special slice IDs: compatibility slice, whole-disk slice, base slice, and whole-slice partition.
- Defines disk ioctl ABI for write-label control, slice info, sync slice info, kernel dump toggle, recluster, media size, sector size, and `DIOCGPART`.
- Defines support limits for disk units, slices, reserved partitions, and in-kernel partitions.
- Defines `struct diskslice` with device, sector offset/size, reserved sectors, type/storage UUIDs, foreign type, flags, label, label ops, per-partition dev pointers, open mask, write-label flag, and open count.
- Defines `struct diskslices` holding global slice array metadata, sector conversion values, and initial slice array.
- Defines `struct partinfo` with byte offset/size, block count/size, reserved blocks, filesystem type, disk geometry, and UUIDs.
- Provides inline minor-number builders/extractors for unit/slice/partition and open-mask helpers.
- Declares MBR/GPT init, open/close/ioctl/size/check helpers, slice structure allocation/free, disk error reporting, and disk bio sorting.

Dependencies:
- Includes types, disklabel, uuid, ioccom, and kernel conf/systm when needed.
- Couples cdev minor layout to disk and devfs device creation.

Notable risks:
- Minor-number bit layout is hard-coded and shared by creation/extraction helpers.
- Reserved block handling protects in-band labels and parent overlaps; filesystem writes must honor it.
- `DIOCGSLICEINFO` exposes `struct diskslices`, so layout compatibility matters for consumers.
