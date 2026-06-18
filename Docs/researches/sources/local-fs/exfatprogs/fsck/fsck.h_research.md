# File Research: sources/local-fs/exfatprogs/fsck/fsck.h

`fsck.h` declares the shared checker state and option bitmask used by `fsck.c` and `repair.c`.

`enum fsck_ui_options` defines repair behavior and auxiliary flags:
- ask, yes, no, auto repair modes.
- `FSCK_OPTS_REPAIR_WRITE` as the write-capable repair-mode mask.
- `FSCK_OPTS_REPAIR_ALL` as all repair policy bits.
- bad filesystem-name ignore, orphan-cluster rescue, and progress bar flags.

`struct exfat_fsck` holds:
- the active `struct exfat *`.
- a reusable directory iterator and cluster buffer descriptors.
- selected options.
- signed MBR operation state.
- dirty and dirty-FAT booleans.
- per-directory filename hash bitmap.
- progress bar state.

The header forward-declares `struct exfat` and `struct exfat_inode`, includes list/utils helpers, and exposes `off_t exfat_c2o(struct exfat *exfat, unsigned int clus)` for cluster-to-device-offset conversion implemented elsewhere.
