# File Research: sources/os/bsd/openbsd-src/sbin/newfs_msdos/newfs_msdos.c

Purpose: Constructs FAT12, FAT16, or FAT32 filesystems on a device. It computes BPB/FAT geometry, optional boot sector content, root directory label entries, FAT initialization, and FAT32 info/backup sectors.

Data models:
- Defines packed byte-array representations for DOS boot sector, BPB, FAT32 extended BPB, extended boot fields, directory entries, and an internal numeric `struct bpb`.
- Uses `mk1`, `mk2`, and `mk4` macros to write little-endian fields into byte buffers.
- Provides standard floppy formats (`160`, `180`, `320`, `360`, `720`, `1200`, `1440`, `2880`).

Option handling:
- Supports dry run `-N`, external boot image `-B`, FAT type `-F`, volume ID `-I`, volume label `-L`, OEM string `-O`, bytes/sector, sectors/FAT, block or cluster size, root directory entries, standard format, heads, info sector, backup sector, media descriptor, FAT count, hidden sectors, reserved sectors, total sectors, sectors/track, and compatibility `-q`/`-t`.
- Validates FAT-type-specific options, label syntax, power-of-two sizes, FAT counts, sector geometry, and media descriptor range.

Geometry and target checks:
- Opens target with `opendev()`, refuses mounted devices unless `-N`, rejects block devices, and warns for non-character targets.
- `getdiskinfo()` reads disklabel or disktab geometry, resolves partition offset/size, and clamps sectors/track to BIOS-compatible values.
- `check_mounted()` compares raw/character device names against current mounts.

FAT layout:
- Chooses FAT12/16/32 automatically if not specified, based on total size, reserved sectors, root directory size, FAT size, and cluster thresholds.
- Computes reserved sectors, root directory sectors, sectors per cluster, sectors per FAT, cluster count, and final total sectors.
- Enforces cluster-count bounds for FAT12/16/32 and warns if FAT size or FAT type limits usable space.

Writing:
- Dry-run prints computed layout and skips writes.
- Non-dry-run writes sectors from LSN 0 through metadata/root region.
- Boot sector is built from supplied boot image or built-in “Non-system disk” boot code.
- FAT32 writes primary and backup boot sectors plus FSInfo sectors when configured.
- FAT sectors are initialized with media descriptor and reserved FAT entries.
- If a label is supplied, a root directory volume label entry is written with DOS timestamp/date.

Support routines:
- `print_bpb()` emits final BPB values.
- `oklabel()` validates DOS label characters.
- `mklabel()` uppercases/pads labels to 11 bytes.
- `setstr()` space-pads OEM/type strings.
