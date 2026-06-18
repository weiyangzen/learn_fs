# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/fscounters_repair.c

This file repairs filesystem summary counters by resetting incore counters to values computed during scrub.

Main operation:
- `xrep_fscounters` requires `fsc->frozen` to be true, traces the reset, then sets:
  - `m_icount`
  - `m_ifree`
  - free data blocks via `xfs_set_freecounter`
  - free realtime extents where applicable.

Important behavior:
- If the filesystem was not frozen, it asserts and returns `-EFSCORRUPTED`; repair must not race live writers.
- Online repair is assumed to run on v5 filesystems with lazy superblock counters, so it does not update `sb_fdblocks`.
- `sb_frextents` is handled carefully because realtime free extent accounting differs with rtgroups and delayed realtime reservations.

Integration:
- Consumes `struct xchk_fscounters` populated by `xchk_fscounters`.
- Forces consistency between computed scrub state and the mount’s in-memory counters.
