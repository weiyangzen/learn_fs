# File Research: sources/local-fs/ntfs-3g/ntfsprogs/ntfsmove.h

## Role

`ntfsmove.h` is the private header for `ntfsmove.c`. It defines placement constants and the shared option structure.

## API Contents

It defines:

- `NTFS_MOVE_LOC_START = -1000`
- `NTFS_MOVE_LOC_BEST = -1001`
- `NTFS_MOVE_LOC_END = -1002`

It also defines `struct options` with device path, file path, target location, force/quiet/verbose flags, no-action mode, and no-dirty mode.

## Integration

`ntfsmove.c` owns a global `static struct options opts` using this type. Positive `location` values represent explicit cluster offsets from `--cluster`; negative constants represent symbolic placement modes.

## Risk Note

The header expresses a richer placement model than the implementation currently honors. `ntfsmove.c` parses these values, but its free-space search ignores them.
