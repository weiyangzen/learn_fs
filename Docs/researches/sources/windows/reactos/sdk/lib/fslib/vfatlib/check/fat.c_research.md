# File Research: sources/windows/reactos/sdk/lib/fslib/vfatlib/check/fat.c

This file implements FAT table loading, entry access/update, cluster ownership tracking, bad cluster handling, orphan reclamation, and FSINFO free-count updates.

Core responsibilities:
- `get_fat` decodes FAT12, FAT16, and FAT32 entries.
- `read_fat` loads one or two FAT copies, resolves mismatches, allocates cluster-owner tracking, and truncates out-of-range links.
- `set_fat` writes a FAT entry and mirrors it to the second FAT if present.
- `bad_cluster`, `next_cluster`, and `cluster_start` provide cluster-chain helpers.
- `set_owner` and `get_owner` track which directory entry owns each cluster.
- `fix_bad` marks unreadable unused clusters bad.
- `reclaim_free` frees allocated but unowned clusters.
- `reclaim_file` creates `FSCK%04dREC` root entries for orphan chains, breaking cycles/cross-links first.
- `update_free` recomputes and optionally writes FAT32 FSINFO free cluster count.

ReactOS-specific behavior:
- Some destructive repairs are gated by `rw`.
- `reclaim_file` only creates recovered files when `rw` is set.
- FSINFO auto-correction is conditional on write access.

Risk points:
- FAT mismatch resolution can overwrite a FAT copy automatically in noninteractive mode.
- `set_owner` treats owner changes as fatal internal errors.
- Orphan recovery mutates FAT chains and root directory entries; it relies on `alloc_rootdir_entry` from `check.c`.
- FAT12 entry updates write two bytes and depend on preserving neighboring nibble correctly.
