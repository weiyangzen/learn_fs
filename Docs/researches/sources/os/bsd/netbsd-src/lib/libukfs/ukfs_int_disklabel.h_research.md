# File Research: sources/os/bsd/netbsd-src/lib/libukfs/ukfs_int_disklabel.h

Private local copy of the on-disk NetBSD disklabel layout.

Key contents:
- Defines:
  - `UKFS_MAXPARTITIONS`
  - `UKFS_DISKMAGIC`
- Defines `struct ukfs__disklabel`, including:
  - disk magic/type/geometry fields,
  - pack/boot name union,
  - spare and hardware fields,
  - checksum,
  - partition count,
  - boot/superblock sizes,
  - fixed partition array.
- Defines nested `struct ukfs__partition` fields:
  - size,
  - offset,
  - filesystem-specific fields,
  - fstype,
  - fragment/segment metadata.
- Declares disklabel scan/checksum helpers.

Role in subsystem:
- Allows `libukfs` to parse disklabel partition metadata portably without including NetBSD kernel headers.
