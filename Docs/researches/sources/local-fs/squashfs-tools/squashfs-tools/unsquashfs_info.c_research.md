# File Research: sources/local-fs/squashfs-tools/squashfs-tools/unsquashfs_info.c

Signal-driven runtime status helper for extraction.

Key behavior:
- Tracks the current pathname via static `pathname`.
- `update_info()` replaces the tracked pathname; `disable_info()` frees and clears it.
- `dump_state()` disables the progress bar, prints queue/cache status for reader, inflate, writer, data cache, and fragment cache, then restores progress.
- `info_thrd()` waits for `SIGQUIT` and `SIGHUP`: first `SIGQUIT` prints the current pathname, and a subsequent signal within the waiting interval triggers a full queue/cache dump.
- `init_info()` starts the info thread.

Dependencies:
- `wait_for_signal()` from `signals.h`.
- Queue/cache dump functions and progress controls from `unsquashfs.c`.
