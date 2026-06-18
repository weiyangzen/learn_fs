# File Research: sources/os/linux/linux-stable/fs/proc/proc_tty.c

Implements `/proc/tty` and TTY driver proc integration.

Key points:
- Creates `/proc/tty`, `/proc/tty/ldisc`, and restricted `/proc/tty/driver`.
- `/proc/tty/drivers` lists pseudo drivers first, then registered `tty_driver` entries.
- Holds `tty_mutex` while iterating `tty_drivers`.
- `show_tty_range()` formats driver name, device path, major/minor range, and driver type/subtype.
- `proc_tty_register_driver()` creates per-driver entries under `/proc/tty/driver` when driver supplies `proc_show`.
- `proc_tty_unregister_driver()` removes the per-driver proc entry.
- `/proc/tty/driver` is user-read/execute only to reduce leakage from serial counters.

Dependencies/contracts:
- Used by TTY core registration/unregistration paths.
- Exposes stable `/proc/tty` userspace-visible hierarchy.
