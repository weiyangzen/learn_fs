# File Research: sources/os/bsd/openbsd-src/sbin/dumpfs/dumpfs.c

## Purpose
Prints detailed UFS/FFS superblock and cylinder-group information, or emits a `newfs` command approximation with `-m`.

## Key Behavior
- Parses `-m`; otherwise dumps filesystem internals.
- Resolves fstab mountpoint arguments through `getfsfile()`.
- Uses `pledge("stdio rpath disklabel")`.
- `open_disk()` opens a device with `opendev()` and probes superblock locations from `SBLOCKSEARCH`, validating UFS1/UFS2 magic, UFS2 self-location, and block size.
- `dumpfs()` prints superblock metadata:
  - magic/time/id
  - geometry and block/fragment sizes
  - optimization/minfree/symlink length
  - cylinder group counts
  - free block/inode summaries
  - allocation layout fields
  - flags, mountpoint, volume name, and swuid
- Reads and prints cylinder summary arrays.
- Iterates all cylinder groups via `dumpcg()`.
- `dumpcg()` prints cylinder group metadata, free summaries, fragment summaries, cluster summaries, inode-use bits, and block-free bits.
- `marshal()` prints a best-effort `newfs` command using values from the existing filesystem.
- `pbits()` prints compact ranges from bitmap fields.

## Notes
This is a diagnostic/introspection tool, not a repair tool. It directly formats UFS structures for operator inspection.
