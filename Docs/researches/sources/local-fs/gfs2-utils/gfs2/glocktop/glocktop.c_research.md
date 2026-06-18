# File Research: sources/local-fs/gfs2-utils/gfs2/glocktop/glocktop.c

This file implements `glocktop`, a GFS2 glock monitor that reads kernel debugfs and procfs state, correlates GFS2 glocks with DLM locks and mounted filesystems, and displays contention interactively with curses or as plain terminal output.

Main behavior is in `main()`: parse options, discover GFS2 mounts and debugfs, initialize curses if requested, allocate large read buffers, then repeatedly scan `debugfs/gfs2/*/glocks` and related `debugfs/dlm/*_{waiters,locks}` files. It supports filtering by glock id, delay/iteration control, held-lock display suppression, DLM display suppression, summary interval, reservation display, help pages, and directory path tracing.

Important components:
- `parse_mounts()` reads `/proc/mounts`, opens GFS2 devices, reads superblocks, and identifies debugfs.
- `parse_dlm_waiters()` and `parse_dlm_grants()` parse DLM debugfs state into fixed arrays.
- `glock_details()` parses glock records, computes summary counts by lock type/state, and decides which glocks to display.
- `show_glock()` prints detailed and friendly views, including lock type, inode type, DLM grants/waiters, holder/waiter pids, and call traces from `/proc/<pid>/stack`.
- `show_details()` maps debugfs fs names to mount devices and can call `show_inode()`/`display_filename()` to classify or trace inode locks.
- Curses helpers handle colors, screen resizing, prompts, title lines, and help.

Dependencies include libgfs2 inode/superblock APIs, curses/termcap, debugfs, DLM configfs/debugfs files, `/proc`, mount table parsing, and Linux block-device ioctls.

Risks and notes:
- The parser relies on fixed kernel debugfs text formats and fixed-width buffers.
- Several arrays are fixed-size (`MAX_LINES`, `MAX_FILES`, glock line width), and not every producer has a clear bounds guard.
- Running may require root privileges, mounted debugfs, readable GFS2 devices, and kernel support for GFS2/DLM debug outputs.
