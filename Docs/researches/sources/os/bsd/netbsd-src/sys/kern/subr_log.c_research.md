# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_log.c

Read completely: 547 lines.

Implements the kernel message-buffer device and sysctls backing `/dev/klog` style access. It manages the circular `kern_msgbuf`, blocking reads, poll/select/kqueue readiness, async SIGIO notification, and `kern.msgbuf*` sysctls.

Core behavior:
- `initmsgbuf()` validates or initializes the persistent ring buffer and enables logging.
- `loginit()` initializes locks, CV/select state, softint, and `kern.msgbufsize`/`kern.msgbuf`.
- `logopen()` enforces a single open reader and sets the async owner to the opener's process.
- `logread()` waits for available bytes unless nonblocking, copies ring contents out in small chunks, and advances `msg_bufr`.
- `logpoll()` and `logkqfilter()` report readable data through select/poll/kqueue.
- `logputchar()` appends one character to the ring, dropping oldest data up to the next line when full.
- `logwakeup()` notifies waiters and schedules SIGIO delivery if async mode is enabled.
- `sysctl_msgbuf()` returns buffer size or a full ring snapshot.

Risks and notes:
- `msg_magic` corruption disables message-buffer logging rather than panicking.
- Sysctl buffer snapshots copy mostly unlocked after grabbing write/end positions.
- Async ownership uses fown helpers, while `FIOASYNC` updates `log_async` without full locking because it is treated as thread-private.
