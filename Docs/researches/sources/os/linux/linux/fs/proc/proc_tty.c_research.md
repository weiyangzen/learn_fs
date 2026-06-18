# File Research: sources/os/linux/linux/fs/proc/proc_tty.c

## Scope

This file implements `/proc/tty`, `/proc/tty/drivers`, `/proc/tty/ldiscs`, and per-driver proc entries under `/proc/tty/driver`.

## Public And Internal APIs Covered

- Driver table formatter: `show_tty_driver()`.
- Per-driver registration: `proc_tty_register_driver()`, `proc_tty_unregister_driver()`.
- Init: `proc_tty_init()`.

## Control Flow And Behavior

- `/proc/tty/drivers` iterates `tty_drivers` under `tty_mutex`.
- The first real driver output is preceded by pseudo-driver lines for `/dev/tty`, `/dev/console`, optional `/dev/ptmx`, and optional `/dev/vc/0`.
- `show_tty_range()` formats each major/minor range and type/subtype classification.
- `proc_tty_register_driver()` creates `/proc/tty/driver/<driver_name>` when the driver has a name, no existing proc entry, and a `proc_show` callback.
- `proc_tty_unregister_driver()` removes the stored proc entry and clears the driver pointer.
- Init creates `/proc/tty`, preserves `/proc/tty/ldisc`, creates restricted `/proc/tty/driver`, and registers `tty/ldiscs` and `tty/drivers`.

## Dependencies And Risks

- Depends on TTY core lists, driver metadata, line discipline seq ops, and proc single-data helpers.
- `/proc/tty/driver` is owner-readable/executable only because serial driver stats can expose keystroke timing information.
