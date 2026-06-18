# File Research: sources/teaching/minix/minix/fs/isofs/main.c

This file is the isofs server entry point and startup logic.

Key behavior:
- Defines `norock` option to disable Rock Ridge interpretation.
- `sef_cb_init_fresh()` initializes options, parses `-o`, clears timezone environment for time conversion, and initializes LMFS buffer pool.
- `sef_cb_signal_handler()` terminates fsdriver on `SIGTERM`.
- `sef_local_startup()` registers init/restart/signal callbacks.
- `main()` sets args, starts SEF, and runs `fsdriver_task(&isofs_table)`.

Role:
- Starts a read-only ISO9660 fsdriver service with optional Rock Ridge support.
