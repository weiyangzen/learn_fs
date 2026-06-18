# File Research: sources/local-fs/dosfstools/src/boot.c

Boot-sector, FSINFO, backup-boot, root-entry, label, and serial handling for FAT filesystems.

Major functions:
- `alloc_rootdir_entry()` allocates a free root-directory entry. For FAT32 root directories it can extend the root cluster chain; for FAT12/16 it scans the fixed root directory. It can generate unique `FSCK%04dREC`-style names.
- `read_boot()` reads and validates the boot sector, derives `DOS_FS` layout fields, identifies FAT12/16/32, checks last-sector accessibility, initializes FAT offsets, root offsets, data area, FAT size, serial, and label.
- `check_backup_boot()` validates or creates FAT32 backup boot sectors and can copy original to backup or backup to original.
- `read_fsinfo()` validates or creates FAT32 FSINFO, records `fsinfo_start`, and loads `free_clusters`.
- `write_boot_label()`, `write_serial()`, and internal `write_boot_label_or_serial()` update boot-sector label or serial for FAT12/16 and FAT32, including backup boot for FAT32.
- `find_volume_de()` scans the root directory for a volume-label directory entry.
- `write_volume_label()` creates or updates the root-directory volume label and sets FAT timestamps, honoring `SOURCE_DATE_EPOCH`.
- `write_label()` writes both boot-sector and root-directory labels.
- `remove_label()` resets boot label to `NO NAME    ` and marks root volume-label entry deleted.
- `pretty_label()` converts the 11-byte DOS label to printable local text using `charconv`.

Important validation logic:
- Rejects zero logical sector size, zero cluster size, unsupported FAT counts, zero FAT size, inaccessible final sector, no data clusters, too many FAT entries, invalid root directory sizing, and filesystems too large for `off_t`.
- FAT32-specific handling validates root cluster/root entries combinations, warns on too-few clusters, checks backup boot, and reads FSINFO.
- FAT12/FAT16 type is inferred from data-cluster thresholds unless Atari variant rules apply.

Dependencies:
- Uses `fs_read`, `fs_write`, and `fs_test` from `io.c`.
- Uses FAT helpers such as `next_cluster`, `cluster_start`, `set_fat`, `get_fat`, and owner tracking.
- Uses `get_choice`, `die`, `alloc`, and label conversion helpers.

Research notes:
- This file is the authoritative translator from raw boot sector fields into the shared `DOS_FS` runtime model.
- Label operations are shared by both `fsck.fat` and `fatlabel`.
