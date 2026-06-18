# File Research: sources/os/bsd/netbsd-src/sys/sys/disklabel.h

Defines the classic NetBSD disklabel on-disk/in-core format, disk type constants, filesystem partition type constants, and kernel disklabel helpers.

Key content:
- Includes machine disklabel parameters unless building tools with `HAVE_NBTOOL_CONFIG_H`.
- `MAXMAXPARTITIONS` capped at 22.
- Device macros: `DISKUNIT`, `DISKPART`, `DISKMINOR`, `MAKEDISKDEV`.
- Magic: `DISKMAGIC`.
- `struct partition`.
- `struct disklabel` with magic fields, drive type/subtype/name, pack/bootstrap union, geometry, spare/alternative cylinders, hardware timing/skew fields, flags, drive-specific data, checksum, partition count, boot/superblock sizes, and partition table.
- Optional `struct olddisklabel`.
- Assembly offsets under `_LOCORE`.
- `DKTYPE_DEFN` list and generated enum/name support.
- `FSTYPE_DEFN` list and generated fsck/mount name support.
- Drive flags and drive-specific aliases.
- `struct format_op` and kernel `struct partinfo`.
- Kernel APIs for reading/writing/converting disklabels, bounds checking, disk errors, and fstype names.

Important behavior:
- Comments document alignment and LP32/LP64 ABI complications.
- Stored on existing disks, so layout compatibility is critical.
