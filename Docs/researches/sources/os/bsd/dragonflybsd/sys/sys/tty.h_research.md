# File Research: sources/os/bsd/dragonflybsd/sys/sys/tty.h

## Summary
Defines DragonFly BSD tty core structures, tty/clist state flags, buffering constants, sleep-address helpers, and kernel tty API prototypes.

## Main Responsibilities
- Defines `struct clist` as a linear character queue with count, max count, head offset, and data buffer.
- Defines kernel-visible `struct tty`, including raw/canonical/output queues, pgrp/session ownership, kqueue state, termios state, watermarks, callbacks, and reference tracking.
- Declares tty state flags such as open/carrier/busy/input blocked/output stopped/zombie/snoop/registered.
- Declares kernel helpers for clists, termios setup, tty read/write/open/close/ioctl, session cleanup, sleeps, wakeups, and registration.

## Important Behavior
The tty object combines device-driver callbacks (`t_oproc`, `t_stop`, `t_param`, `t_unhold`) with line discipline and queueing state. Sleep-channel macros intentionally use distinct addresses inside the tty object to avoid aliasing wakeups.

## Risks
The structure is a shared kernel ABI surface for tty drivers and line disciplines. Many state bits encode historical behavior, and incorrect locking or queue watermark handling can break blocking I/O, pty operation, or terminal session semantics.
