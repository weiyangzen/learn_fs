# File Research: sources/os/bsd/freebsd-src/sbin/recoverdisk/recoverdisk.c

Disk/file recovery utility that copies readable ranges and retries failures at smaller block sizes.

Key elements:
- Tracks pending byte ranges as `struct lump { start, len, pass }` in a TAILQ.
- Tracks throughput per minute, quarter-hour, hour, and day for verbose reporting.
- `report` prints progress, pending count, success ratio, duration, histogram, and recent-period read totals.
- `new_lump` appends unread/retry work.
- `save_worklist` fsyncs destination, writes pending lumps to a temp worklist, and renames atomically.
- `read_worklist` restores pending ranges from a saved worklist.
- `write_buf` writes recovered or unreadable-pattern bytes at the original offset and saves the worklist on write errors.
- `attempt_one_lump` reads the first pending range using big/medium/small size by pass, writes successes, logs successes, accounts progress, and on read error writes the unreadable pattern, creates a smaller retry lump, and advances/removes the current lump.
- `determine_total_size` uses explicit `-t`, device media size, or regular file size.
- `determine_read_sizes` chooses small/medium/big read sizes from ioctl sector/stripe/firmware geometry or defaults, enforcing multiples.
- `monitor_read_sizes` adapts to repeated failures by shrinking big/medium reads.
- `main` parses read size, interval, log, pause, worklist, total size, unreadable pattern, and verbose options; opens source/destination; initializes buffers and worklist; loops until complete or SIGINT; saves worklist and reports final status.

Dependencies:
- FreeBSD disk ioctls, `TAILQ`, `pread`/`pwrite`, `fdatasync`, `ftruncate`, terminal size/ioctl, math `round`, and POSIX signals.

Research notes:
- The destination is pre-sized with `ftruncate`; unreadable regions can be filled with `_UNREAD_` or a user pattern.
- SIGINT is only specially handled when a write worklist is requested.
- The hour/day TAILQ initializers name `quarter` instead of their own heads in the static declarations, which is unusual and worth checking if modifying this code.
