# File Research: sources/teaching/minix/minix/fs/mfs/main.c

`main.c` is the MFS service entry point and SEF integration layer. `main` records command-line arguments, performs local SEF startup, and hands control to `fsdriver_task(&mfs_table)`.

`sef_local_startup` registers fresh-start initialization, stateful restart handling, and signal handling. `sef_cb_init_fresh` enables VM cache use in libminixfs, initializes inode reference counters and the disabled diagnostic `cch` array, builds the inode cache free/hash structures, and creates the buffer pool using `DEFAULT_NR_BUFS`. `sef_cb_signal_handler` handles only `SIGTERM`, syncing MFS state before asking fsdriver to terminate.

The disabled `cch_check` block is a historical consistency aid for tracking inode reference deltas across requests; it is not compiled.
