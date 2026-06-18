# File Research: sources/os/bsd/openbsd-src/sbin/fsck_msdos/boot.c

## Scope

Boot-sector and FAT32 FSInfo parser/writer for `fsck_msdos`. It decodes the BIOS parameter block into `struct bootblock`, validates filesystem geometry, checks FAT32 backup boot blocks, and can repair/write FSInfo counters.

## Main APIs

- `readboot(dosfs, boot)` reads and validates the boot sector and FAT32 metadata.
- `writefsinfo(dosfs, boot)` updates FAT32 FSInfo free-cluster and next-free fields.

## Control Flow

`readboot()` reads sector zero using the disklabel sector size and requires the 0x55aa signature. It decodes BPB fields, validates sector size, cluster size, FAT count, FAT sector count, and filesystem version. FAT32 is detected by zero root-directory entries; FAT32-specific fields include active FAT, root cluster, FSInfo sector, and backup boot sector.

For FAT32, it validates FSInfo signatures and offers to repair them. It reads and compares the backup boot block signature and BPB/extended FAT32 fields. It then computes cluster offset, sector count, cluster count, FAT type mask, number of FAT entries, and cluster size. It rejects non-FAT32 filesystems too large for FAT12/16 and FATs too small for the cluster count.

`writefsinfo()` rereads the FSInfo area, patches `FSFree` and `FSNext`, writes it back, and intentionally returns success rather than `FSBOOTMOD` because FSInfo is often stale.

## Dependencies

- Uses global `lab.d_secsize` from `check.c`.
- Uses `ask()`, `pfatal()`, `pwarn()`, and `xperror()` from shared fsck utilities.
- Defines values consumed by `fat.c` and `dir.c` through `struct bootblock`.

## Risks And Edge Cases

- FSInfo validation reads two sectors when needed to cover both signature areas.
- Backup boot comparison ignores boot code and compares only BPB/extended metadata plus signature.
- `ClusterOffset` is allowed to be a signed-style arithmetic result stored unsigned; invalid oversize is caught later.
