# File Research: sources/os/bsd/dragonflybsd/sys/kern/subr_disklabel32.c

Legacy BSD 32-bit disklabel operations implementation for DragonFly disk slices.

Key responsibilities:
- Reads disklabel32 metadata from `LABELSECTOR32`, scanning the sector at long-word increments for a valid magic/checksum pair.
- Converts legacy absolute on-disk partition offsets to slice-relative in-core offsets via `l32_fixlabel()`.
- Exposes partition bounds, filesystem type, partition count, pack name, clone/virgin label creation, label writing, and label freeing through `disklabel32_ops`.
- Validates new labels, including magic/checksum, open partition compatibility, raw partition offset, slice bounds, and partition sizes.
- Writes labels by reading the existing label sector, finding an existing valid label location, replacing it, fixing offsets for disk format, and writing the sector back.
- Creates compatibility labels for unlabeled media, including raw partition and optional `a` partition.

Important behavior:
- In-core labels are always slice-relative, while on-disk 32-bit labels are adjusted back to absolute offsets when written.
- Open partitions cannot move or shrink; omitted filesystem metadata can inherit from the old open partition.
- The raw partition must start at offset 0 after in-core normalization.

Dependencies:
- Depends on disk slice state, UFS constants for boot/superblock sizes, `dkcksum32()`, pbuf synchronous I/O, and legacy disklabel structures.

Notable risks:
- No UUID information is available from disklabel32, so UUID aliases cannot come from this label format.
- The write path requires finding an existing valid label in the sector, making first-write or corrupted-label replacement awkward through this API.
- Size and offset fields are 32-bit-sector based and carry legacy 2TB-era limitations.
