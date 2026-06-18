# File Research: sources/os/bsd/openbsd-src/sbin/fsck_ffs/setup.c

## Scope

Filesystem setup and superblock validation for `fsck_ffs` and `fsdb`. It opens devices, reads disklabels, finds and validates primary or alternate superblocks, fixes derived superblock fields, reads summary information, and allocates fsck working maps.

## Main APIs

- `setup(dev, isfsdb)` prepares a filesystem for checking or editing.
- `readsb(listerr)` locates and validates a superblock.
- `badsb()` reports bad-superblock reasons.
- `calcsb()` derives a prototype FFS superblock from disklabel partition geometry to search alternates.
- `getdisklabel()` reads `DIOCGDINFO`.
- `cmpsb()` compares stable primary/alternate superblock fields.

## Control Flow

`setup()` opens the raw device read-only, resolves canonical device names, applies `unveil()`/`pledge()` depending on caller/root state, optionally opens for write, initializes superblock buffers, and determines sector size. It reads the superblock via `readsb()`. If primary lookup fails and interactive recovery is possible, it calculates prototype geometry and searches known alternate locations and per-cylinder-group backup superblocks for UFS1/UFS2.

After a usable superblock is found, clean filesystems can be skipped. Otherwise it calculates `maxfsblock`, `maxino`, and max file size, validates and optionally repairs superblock fields including optimization policy, minfree, sector counts, masks, shifts, inode format, maxfilesize, maxsymlinklen, q masks, cgsize, `INOPB`, and `NINDIR`. It then reads cylinder summary blocks and allocates `blockmap`, `inostathead`, directory sort tables, directory hash heads, and buffer caches.

`readsb()` validates magic, UFS1/UFS2 locations, ncg/cpg/ncyl bounds, superblock size, power-of-two block and fragment sizes, and primary-vs-last-alternate consistency.

## Dependencies

- Device helpers from `fsutil`: `opendev()`, `blockcheck()`, `unrawname()`, `setcdevname()`.
- FFS disklabel and geometry macros.
- Buffer and allocation helpers from `utilities.c`.

## Risks And Edge Cases

- Alternate superblock search only proceeds when not preening and a prototype can be calculated.
- `cmpsb()` intentionally ignores dynamic fields, comparing only structural fields expected to match backups.
- Fixing alternate superblock mirror fields marks `asblk` dirty and can flush it early.
- `isfsdb` changes pledge behavior and skips some normal fsck assumptions.
