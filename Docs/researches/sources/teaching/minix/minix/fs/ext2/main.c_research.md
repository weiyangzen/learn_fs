# File Research: sources/teaching/minix/minix/fs/ext2/main.c

This file is the ext2 server entry point and SEF startup handler.

Key behavior:
- Defines mount/server options: `sb`, `orlov`, `oldalloc`, `mfsalloc`, `reserved`, `prealloc`, `noprealloc`.
- `main()` registers args, starts SEF, detects CPU endian, asserts little-endian CPU, then runs `fsdriver_task(&ext2_table)`.
- `sef_cb_init_fresh()` initializes defaults, parses `-o` options, enables VM cache usage, initializes inode table/cache, and creates a small initial LMFS buffer pool.
- `sef_cb_signal_handler()` handles `SIGTERM` by syncing and terminating the fsdriver.

Default options:
- Orlov enabled.
- MFS allocator disabled.
- Reserved block usage disabled.
- Alternate superblock offset zero.
- Preallocation disabled by default.

Notable constraint:
- The server asserts little-endian operation despite conversion helpers existing elsewhere.
