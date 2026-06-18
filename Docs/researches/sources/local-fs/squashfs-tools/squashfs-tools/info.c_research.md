# File Research: sources/local-fs/squashfs-tools/squashfs-tools/info.c

Implements signal-driven runtime diagnostics for `mksquashfs`.

Public functions:
- `disable_info()`
- `update_info(struct dir_ent *)`
- `init_info()`

Behavior:
- Tracks the current directory entry in a static `ent`.
- `print_filename()` prints the current file path via `progressbar_info()`.
- `dump_state()` disables the progress bar and prints queue/cache/thread status across the whole compression pipeline.
- `info_thrd()` waits for `SIGQUIT` and `SIGHUP`.
  - First `SIGQUIT` prints current filename and opens a short waiting window.
  - A second signal during that window, or SIGHUP, dumps full queue/cache/thread state.
- `init_info()` starts the info thread.

Dependencies:
- Uses global pipeline objects from other modules: queues, caches, reader state, and thread dump helpers.

Key role: operational introspection while long `mksquashfs` runs are active.
