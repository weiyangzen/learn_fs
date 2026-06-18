# File Research: sources/os/bsd/freebsd-src/sbin/fsck_ffs/fsutil.c

This file provides the checker’s utility layer: prompt handling, inode-state lookup, buffer cache, block I/O, cylinder group validation/rebuild helpers, allocation helpers, final cleanup, I/O stats, and fatal/warning output.

Key behavior:
- `fsutilinit()` resets per-run I/O and slow-I/O counters.
- `ftypeok()` validates legal UFS inode file types.
- `reply()` implements interactive yes/no policy, including `-n`, `-y`, read-only, and preen restrictions.
- `inoinfo()` returns per-inode state from cylinder-group-indexed `inostathead`.
- `bufinit()`, `getdatablk()`, `getblk()`, `brelse()`, `binval()`, and `flush()` implement a typed LRU buffer cache.
- `cglookup()`, `cgdirty()`, and `flushentry()` manage cached cylinder group blocks and hashes.
- `flush()` handles type-specific writeback: superblocks through `sbput`, cylinder groups through `cgput`, inode hash repair, snapshot copy-on-write, and raw block writes.
- `snapflush()` forces pending snapshot copies before cylinder-group rebuilds.
- `cg_write()` recomputes SUJ cylinder-group fragment/cluster summaries before writing.
- `rwerror()`, `pfatal()`, `pwarn()`, and `panic()` centralize error policy.
- `ckfini()` performs final writeback, clean/dirty marking, resource cleanup, and descriptor close.
- `blread()`, `blwrite()`, `blerase()`, and `blzero()` implement raw device I/O and optional delete/zero of free space.
- `check_cgmagic()` validates cylinder group magic, index, sizes, offsets, initialized inode counts, and CRC when enabled.
- `rebuild_cg()` reconstructs a cylinder group header so later passes can rebuild maps.
- `allocblk()` and `std_checkblkavail()` allocate free fragments, updating block maps and cylinder group summaries.
- `chkfilesize()` enforces UFS1/UFS2/kernel maximum file size and `MAXDIRSIZE`.
- `slowio_start()` / `slowio_end()` throttle background fsck I/O.
- `getpathname()` reconstructs a path by walking `..` and parent directories.
- `dofix()` encapsulates salvage/fix decision state for an `inodesc`.

Important invariants:
- `ckfini()` flushes in a strict order: cylinder groups, indirect/directory/EA/data blocks, inode blocks, then superblock. This preserves metadata reachability during partial truncation repair.
- SUJ recovery avoids recycling dirty buffers when doing so would force premature writes.
- Dirty writes in read-only mode are treated as internal fatal errors.
- Background mode uses sysctls for live metadata adjustment and marks `FS_NEEDSFSCK` when background repair cannot proceed.
