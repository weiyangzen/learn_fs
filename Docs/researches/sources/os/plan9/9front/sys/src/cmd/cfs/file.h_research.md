# File Research: sources/os/plan9/9front/sys/src/cmd/cfs/file.h

Declarations for cached file data operations.

Key declarations:
- `fread(Icache*, Ibuf*, char*, ulong, long)`
- `fwrite(Icache*, Ibuf*, char*, ulong, long)`

Dependencies:
- Uses inode cache types from `inode.h`.

Research notes:
- This header exposes only the byte-level cache read/write API used by `cfs.c`.
