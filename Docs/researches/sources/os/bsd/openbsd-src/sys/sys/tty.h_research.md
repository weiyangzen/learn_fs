# File Research: sources/os/bsd/openbsd-src/sys/sys/tty.h

Defines core tty kernel state plus a small amount of public ABI. It includes `termios`, queues, select state, and timeouts. Public pieces include tty sysctl ids, `struct ptmget`, `PTMGET`, `/dev/ptm`, and tty group id.

`struct tty` holds raw/canonical/output clists, statistics, device id, state/flags, foreground process group/session, select state, termios, window size, driver callbacks, watermarks, restart timeout, and timestamp. Kernel declarations cover clist operations, tty read/write/ioctl/open/close, wakeups, line editing, flow/modem handling, controlling tty operations, PPP/NMEA/MSTS/EndRun line discipline hooks, and tty allocation/free.
