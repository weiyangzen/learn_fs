# File Research: sources/os/plan9/9front/sys/src/cmd/gefs/ream.c

gefs formatter and grower for block devices.

Key responsibilities:
- Creates initial arena headers, allocation logs, root tree, `adm` tree, users file, snapshot tree, and superblock copies.
- Initializes labels `empty`, `adm`, and mutable `main`.
- Writes default `/adm/users` content using the requested ream user.
- Splits a device into 8 to 32 arenas for initial formatting.
- Adds four new arenas when growing a filesystem.

Important behavior:
- Requires at least `128 MiB + Blksz` for ream.
- Leaves two blocks at each arena start for arena header/footer.
- Writes both primary superblock at block 0 and backup superblock near device end.
- `growfs()` rewrites the backup superblock at the new end after extending arena metadata.

Notable risks:
- `reamfs()` has duplicated `dropblk()` calls for several blocks after they were already dropped, which is suspicious unless reference counts were intentionally held.
- Grow requires at least 64 MiB of new arena space.
