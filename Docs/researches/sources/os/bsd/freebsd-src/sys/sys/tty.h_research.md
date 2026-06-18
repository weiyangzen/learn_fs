# File Research: sources/os/bsd/freebsd-src/sys/sys/tty.h

Central kernel TTY structure and public TTY management interface.

Key responsibilities:
- Defines `struct tty`, including lock ownership, global list linkage, flags, revoke count, input/output queues and watermarks, wait condition variables, poll state, async I/O state, termios/window state, init/lock termios states, driver and hook pointers, process/session ownership, softc pointers, device node, and SIGINFO print buffer.
- Defines TTY flags for device naming, init/lock/callout devices, open modes, gone/openclose, async I/O, literal input, high watermarks, flow stopped, exclusive access, bypass path, zombie, hook presence, and busy state.
- Defines userland export `struct xtty` for `kern.ttys`.
- Under `_KERNEL`, declares allocation, locking, device creation, signal, wait/wakeup, output, ioctl, window-size, console, flush, watermark, dev-name, status, console selection, and pty allocation helpers.
- Includes line discipline, device switch, and hook headers for kernel users.

Dependencies:
- Includes queue, locks, mutexes, condition variables, selinfo, termios, tty ioctl, and tty queue headers.

Notable risks:
- TTY state is heavily lock-annotated; fields marked `(t)`, `(l)`, and `(c)` have different lifetime and synchronization rules.
- Flag values are shared with debugging and `pstat(8)`, so renumbering or semantic changes can break observability.
