# File Research: sources/os/bsd/netbsd-src/sys/kern/tty_pty.c

## Purpose

`tty_pty.c` implements NetBSD's pseudo-terminal master and slave character devices, including dynamic pty allocation, master/slave I/O, packet/user-control modes, remote mode, polling/kqueue readiness, and pty-specific ioctls.

## Main Responsibilities

- Defines master `ptc_cdevsw` and slave `pts_cdevsw` device switches.
- Maintains the dynamically growable `pt_softc` table and `npty`/`maxptys` limits.
- Allocates per-pty `struct tty` objects and select state.
- Implements slave open/close/read/write/poll via the tty line discipline.
- Implements master open/close/read/write/poll and kqueue filters.
- Bridges tty output from slave to master and master input to slave.
- Implements pty ioctls: `TIOCPKT`, `TIOCUCNTL`, `TIOCREMOTE`, `TIOCPTSNAME`, `TIOCGRANTPT`, `TIOCSIG`, and pty-specific `FIONREAD`.

## Core Data Model

Each `pt_softc` holds a `struct tty *`, pty flags, master-side select state, packet-mode pending byte, and user-control byte. `pt_softc_mutex` protects table growth and installation; normal tty I/O state is protected by `tty_lock`.

`pty_check()` validates a requested minor, grows the pty table up to `maxptys`, allocates missing softc/tty structures, initializes select state, and attaches the tty.

## Slave Side

`ptsopen()` initializes default termios state on first open, waits for carrier unless nonblocking, opens the line discipline, and wakes the master. `ptsclose()` closes the line discipline, calls `ttyclose()`, and wakes master waiters.

`ptsread()` normally delegates to the line discipline read path; in remote mode it reads from `t_canq` with a trailing NUL delimiter convention. `ptswrite()` delegates to the line discipline write path when the master is present.

## Master Side

`ptcopen()` claims an unused pty by setting `t_oproc = ptsstart`, marks carrier through the line discipline modem hook, and clears pty flags. `ptcclose()` drops carrier and clears `t_oproc`.

`ptcread()` returns pending packet/control bytes first, then drains slave output from `t_outq`. `ptcwrite()` injects master input into the slave side, either as remote-mode records or by feeding each byte to the line discipline receive routine.

`ptsstart()`, `ptsstop()`, and `ptcwakeup()` translate tty output/stop/flush state into master-side wakeups and packet-mode notifications.

## Ioctl Behavior

`ptyioctl()` handles pty-specific controls before falling through to line discipline and common tty ioctls. Packet mode and user-control mode are mutually exclusive. Remote mode flushes tty queues. `TIOCSIG` validates the signal, optionally flushes queues, marks SIGINFO state, and queues a tty signal. When external processing and packet mode are enabled, termios-setting ioctls generate `TIOCPKT_IOCTL`.

## Concurrency Notes

The pty table is protected separately from tty state. I/O paths carefully drop `tty_lock` while copying to/from user memory and re-check open/carrier state after reacquiring it.
