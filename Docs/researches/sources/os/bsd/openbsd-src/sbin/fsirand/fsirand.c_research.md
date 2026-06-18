# File Research: sources/os/bsd/openbsd-src/sbin/fsirand/fsirand.c

## Scope

FFS inode-generation and filesystem-id randomizer. It can print current generation values or rewrite `fs_id` and every inode `di_gen`.

## Main APIs

- `main()` parses `-b`, `-f`, `-p`, raises data-size limit, and runs `fsirand()` for each device.
- `fsirand(device)` performs all superblock validation, optional printing, randomization, and writes.
- `usage()` reports syntax.

## Control Flow

The utility opens the device read-only for print mode or read-write otherwise, optionally reads disklabel sector size, pledges `stdio`, searches known superblock locations, validates FFS magic/location/size/format, rejects non-clean filesystems unless forced, and verifies all backup superblocks.

For modern inode formats, non-print mode randomizes `fs_id[0]` with current time and `fs_id[1]` with `arc4random()`, writes the primary superblock, then writes each backup superblock. It reads each cylinder group’s inode area into a reusable buffer and either prints generation numbers or assigns new random generations for all inodes at or above `ROOTINO`, then writes modified inode buffers.

## Dependencies

- Uses FFS/UFS structures and macros including `SBLOCKSEARCH`, `ino_to_fsba()`, and `cgsblock()`.
- Uses `opendev()` from `libutil`.
- Uses disklabel `DIOCGDINFO` unless `-b` ignores labels.

## Risks And Edge Cases

- Refuses old `FS_42POSTBLFMT`.
- Clean-check can be bypassed with `-f`; otherwise it requires `FS_ISCLEAN`.
- Writes the primary superblock at `SBOFF`, while searched superblock location may be from `SBLOCKSEARCH`.
- Reads entire `fs_ipg` inode set per cylinder group, which can be large.
