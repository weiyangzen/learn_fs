# File Research: sources/os/bsd/freebsd-src/sbin/dump/dump.h

## Purpose
Shared global declarations, macros, prototypes, and dump-date structures for the UFS `dump` utility.

## Main Elements
- Inode map globals and macros: `usedinomap`, `dumpdirmap`, `dumpinomap`, plus `SETINO`, `CLRINO`, and `TSTINO`.
- Global dump state: disk/tape names, dumpdates path, levels, flags, file descriptors, media sizing, cache size, rsync-friendly mode, operator notification, tape counters, filesystem superblock, device/tape block shifts, and timing.
- Function prototypes:
  - Operator interface: `broadcast()`, `infosch()`, `lastdump()`, `msg()`, `msgtail()`, `query()`, `quit()`, `timeest()`, `unctime()`.
  - Mapping/traversal: `mapfiles()`, `mapdirs()`, `blkread()`, `cread()`, `dumpino()`, `dumpmap()`, `writeheader()`, `getino()`.
  - Tape/output: `alloctape()`, `close_rewind()`, `dumpblock()`, `startnewtape()`, `trewind()`, `writerec()`.
  - Exit/signal/fstab/remote dump helpers.
- Exit status constants: `X_FINOK`, `X_STARTUP`, `X_REWRITE`, `X_ABORT`.
- Dumpdates records: `struct dumpdates`, `ddatev`, `nddates`, iteration macro, file format constants.
- Fallback `_PATH_FSTAB`.

## Dependencies And Integration
Included by dump source files to share the program’s global state across main, traversal, tape, operator, remote, cache, and date modules.

## Risk Notes
The utility is built around many mutable globals, so ordering and initialization across modules matter. Inode map macros assume valid inode numbers starting at one and byte-addressed maps sized by `mapsize`.
