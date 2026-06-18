# File Research: sources/os/plan9/9front/sys/src/cmd/cwfs/wren.c

Purpose: Plain disk/file-backed block device implementation for cwfs `Devwren`.

Key structures:
- Private `Wren`: native block size, native block count, multiplier to cwfs `RBUFSIZE`, and max logical block count.

Key behavior:
- `dataof()` maps a configured path to either the path itself or `path/data` if it is a directory.
- `wreninit()` allocates private geometry, resolves `/dev/sdXX/data` or configured file, opens it read-write, finds block size via `inqsize()`, falls back to 512-byte sectors when needed, and derives logical block count.
- `wrensize()` returns logical block capacity.
- `wrenread()` and `wrenwrite()` bounds-check logical blocks and use `pread`/`pwrite` of `RBUFSIZE` bytes.

Notable details:
- Errors increment `cons.nwrenre` and `cons.nwrenwe`.
- This is the normal I/O path for disks and for jukebox optical drives once media is loaded.
