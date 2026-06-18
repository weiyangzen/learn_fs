# File Research: sources/os/bsd/freebsd-src/sys/kern/tty_pts.c

## Purpose
Implements pseudo-terminal master support and `posix_openpt()`, allocating PTY pairs with a master file object and a slave TTY device under `/dev/pts/N`.

## Main Structures and State
- `pts_pool`: unit-number allocator.
- `struct pts_softc`: per-PTY state, unit, packet-mode flags, unread packet byte, master-side CVs/poll state, optional external master cdev, and credential for resource accounting.
- `ptsdev_ops`: file operations for the PTY master.
- `pts_class`: tty driver switch for the slave side.

## Master File Operations
- `ptsdev_read()` reads slave output through `ttydisc_getc_uio()`, emits packet-mode bytes first, blocks on `pts_outwait`, and handles nonblocking/EIO state.
- `ptsdev_write()` copies master input from userspace, feeds it into the line discipline with `ttydisc_rint_simple()`, blocks on input space, and wakes slave readers.
- `ptsdev_ioctl()` implements master-specific commands such as `FIODTYPE`, `FIONREAD`, `FIODGNAME`, `TIOCGPTN`, `TIOCGPGRP`, `TIOCGSID`, `TIOCPTMASTER`, `TIOCSIG`, `TIOCPKT`, Linux-friendly `TIOCGETA`, and redirects other ioctls to the slave tty.
- Poll/kqueue use reversed master-side semantics: master read watches slave output; master write watches slave input capacity.
- `ptsdev_stat()` fabricates character-device stat data from the slave or external master cdev.
- `ptsdev_close()` marks the tty gone and closes the original vnode if `/dev/ptmx` or old pty open changed the file type.

## Driver-Side Hooks
- `ptsdrv_outwakeup()` wakes master readers.
- `ptsdrv_inwakeup()` wakes master writers.
- `ptsdrv_open()` clears `PTS_FINISHED`; `ptsdrv_close()` sets it and wakes both sides.
- `ptsdrv_pktnotify()` accumulates packet-mode events and resolves conflicting start/stop flags.
- `ptsdrv_free()` releases unit number, RACCT/RLIMIT accounting, credentials, poll/kqueue resources, optional external cdev, and softc memory.

## Allocation
- `pts_alloc()` enforces `RACCT_NPTS` and `RLIMIT_NPTS`, allocates a unit, softc, tty, poll lists, exposes `pts/<unit>`, and initializes the master file as `DTYPE_PTS`.
- `pts_alloc_external()` supports old/external master cdev allocation without assigning a normal unit.
- `sys_posix_openpt()` validates flags, allocates a file descriptor/file, calls `pts_alloc()`, and returns the master fd.
- `pts_init()` initializes the unit allocator.

## Notes and Risks
- Packet mode multiplexes control notifications as leading bytes on master reads.
- Several comments document historical/Linux/POSIX compatibility behavior, including `fstat()` expectations and avoiding master-side drain deadlocks.
