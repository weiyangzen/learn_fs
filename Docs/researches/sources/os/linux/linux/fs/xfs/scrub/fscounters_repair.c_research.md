# File Research: sources/os/linux/linux/fs/xfs/scrub/fscounters_repair.c

Repairs filesystem summary counters by resetting in-core counters to values computed during the required scrub phase.

Main function:
- `xrep_fscounters` requires `fsc->frozen` to be true, traces the reset, sets `m_icount`, `m_ifree`, and free block counters from scrub-computed values, and updates realtime free extent counters when appropriate.

Important details:
- Repair depends on the setup/check phase freezing the filesystem, preventing concurrent counter changes.
- Online repair only supports v5 filesystems with lazy data-block superblock counters, so it does not update `sb_fdblocks` directly.
- `sb_frextents` is updated directly for non-rtgroup realtime filesystems because its lazy-counter behavior differs.
