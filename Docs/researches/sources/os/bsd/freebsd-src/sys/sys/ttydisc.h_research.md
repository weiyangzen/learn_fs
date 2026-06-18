# File Research: sources/os/bsd/freebsd-src/sys/sys/ttydisc.h

Kernel TTY line discipline interface.

Key responsibilities:
- Requires inclusion through `sys/tty.h`.
- Declares top-half routines for open, close, bytes-available query, read, write, canonicalization, and optimization.
- Declares bottom-half routines for modem state, receive-character paths, simple/bypass receive, receive completion, receive polling, output getc, UIO getc, and output poll.
- Defines receive error flags for framing, parity, overrun, and break.
- Provides inline read/write poll helpers that assert the TTY lock and query input canonicalized bytes or output queue space.

Dependencies:
- Depends on `struct tty`, `uio`, queue helpers, and TTY locking macros.

Notable risks:
- The bypass receive path depends on `TF_BYPASS`; line discipline optimization must keep flag state consistent with termios processing needs.
- Bottom-half functions are commonly called from driver contexts and must honor locking and wakeup expectations.
