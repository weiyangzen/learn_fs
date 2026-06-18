# File Research: sources/os/linux/linux-stable/fs/xfs/scrub/fscounters.h

This header defines the scrub-time state for filesystem counter checking and repair.

Key structure:
- `struct xchk_fscounters`
  - `sc`: owning scrub context.
  - `icount`, `ifree`, `fdblocks`: computed expected global counters.
  - `frextents`, `frextents_delayed`: realtime free extent accounting.
  - `icount_min`, `icount_max`: valid inode count bounds from filesystem geometry.
  - `frozen`: whether scrub/repair froze the filesystem.

Integration:
- Used by `fscounters.c` for checking and by `fscounters_repair.c` for resetting counters from computed values.
