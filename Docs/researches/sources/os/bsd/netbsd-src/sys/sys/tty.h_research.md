# File Research: sources/os/bsd/netbsd-src/sys/sys/tty.h

Read completely: 340 lines.

Defines kernel tty state, queues, flags, and tty helper APIs.

Key elements:
- `struct clist` represents tty ring-buffer queues, with optional quote tracking.
- `enum ttysigtype` identifies queued tty signal classes.
- `struct tty` stores raw/canonical/output queues, condition variables, line discipline, device id, state/flags, session and process group, select state, termios, window size, output/hardware callbacks, watermarks, signal queues, driver softc, and refcount.
- Defines tty priorities, queue sizing/watermark macros, dialout/callout minor decoding, and many `TS_*` state bits.
- Defines character classification constants, modem control commands, tty input error/quote flags, controlling-terminal/background macros, and `ttylist_head`.
- Kernel declarations cover clist operations, tty open/close/read/write/ioctl/poll, line editing, flush/wait/sleep, signal dispatch, attach/detach/init/allocation, locking, and control-character helpers.
- Exposes global tty locks, console tty pointer, tty count, and default tty characters.

Risks and notes:
- `struct tty` is central kernel state shared by drivers, line discipline, session/job-control code, and select/poll.
- Queue and lock invariants are critical; comments warn not to manipulate clist internals outside tty support code.
