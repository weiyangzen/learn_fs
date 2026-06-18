# File Research: sources/os/bsd/freebsd-src/sbin/fsck_ffs/globs.c

This file defines most global storage declared in `fsck.h` and initializes per-filesystem checker state.

Key behavior:
- Defines read counters/timers, superblock buffer `sblk`, current directory buffer `pdirbp`, directory cache counters, sysctl MIB arrays, global command structure, device/mode flags, block/inode counters, signal flags, duplicate lists, inode state lists, and zero inode `zino`.
- `fsckinit()` resets these globals before checking each filesystem.
- Initializes file descriptors to `-1`, `lfname` to `lost+found`, `lfmode` to `0700`, `resolved`/`havesb`/`fsmodified` state, counters, and zero dinodes.

Important interactions:
- `main.c` calls `fsckinit()` for each target filesystem.
- The globals are shared by all passes, directory repair, inode traversal, setup, and fsutil code.
