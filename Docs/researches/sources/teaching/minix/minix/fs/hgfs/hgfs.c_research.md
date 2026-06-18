# File Research: sources/teaching/minix/minix/fs/hgfs/hgfs.c

This file is the HGFS server glue layer between `libsffs` and `libhgfs`.

Key behavior:
- Defines `sffs_params params` and option parsing for prefix, uid, gid, file mask, directory mask, and case sensitivity.
- `sef_cb_init_fresh()` initializes defaults, parses `-o`, initializes HGFS library, then initializes SFFS with the HGFS operation table.
- `sef_local_startup()` registers SEF init and SFFS signal handler.
- `main()` sets environment args, starts SEF, runs `sffs_loop()`, then cleans up HGFS.

Dependencies:
- `hgfs_init()` provides an `sffs_table`.
- `sffs_init()` exposes HGFS through the shared-folder filesystem abstraction.

Failure handling:
- Reports disabled shared folders on `EAGAIN`.
- Cleans up HGFS if SFFS initialization fails.
