# File Research: sources/os/bsd/openbsd-src/sbin/fsck/fsck.c

Implements the generic `fsck` front-end that selects filesystems and execs filesystem-specific helpers such as `fsck_ffs` or `fsck_ext2fs`.

Main flow:
- Raises data-size limits, initializes root-device state, unveils `/dev`, `/etc/fstab`, and fsck helper directories, then pledges restricted capabilities.
- Parses global flags such as debug, verbose, preen, no/yes answers, alternate superblock, type selection, network filtering, parallel limit, and per-filesystem `-T type:options`.
- If no operands are given, scans `/etc/fstab` through `checkfstab`.
- If operands are given, resolves device names, DUIDs, mount points, and fstab entries, then checks each requested target.

Selection and dispatch:
- `isok` filters fstab entries by pass number, rw/ro/rq type, network option, and selected filesystem type list.
- `checkfs` normalizes `ufs` to `MOUNT_UFS`, constructs `fsck_<vfstype>` argv, combines global/per-type options, forks, and execs helper binaries from `/sbin` or `/usr/sbin`.
- `maketypelist` supports include and `no...` exclude type lists.
- `mangle` converts comma-separated options into helper argv, splitting `-x=value` into separate option/value arguments.
- `addoption` stores per-filesystem option strings in a TAILQ.

The file does not repair filesystems itself; it is an option parser, fstab selector, and subprocess launcher for concrete fsck implementations.
