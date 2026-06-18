# File Research: sources/os/linux/linux-stable/fs/proc/loadavg.c

Implements `/proc/loadavg`.

Key points:
- Reads avenrun via `get_avenrun()`.
- Formats 1, 5, and 15 minute load averages, running/thread counts, and last PID cursor in the current active PID namespace.
- Registers `loadavg` as a permanent single proc file.

Dependencies/contracts:
- Uses scheduler load accounting and PID namespace IDR cursor.
