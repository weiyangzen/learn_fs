# File Research: sources/os/bsd/openbsd-src/sys/kern/tty.c

Core OpenBSD terminal subsystem implementation. It provides the default termios line discipline, character input processing, output processing, generic tty ioctls, read/write paths, kqueue filters, job-control behavior, flow control, tty allocation/freeing, and tty sysctl statistics.

Global state:
- `char_type[]`: classification/parity table used by input, output, erase, and column tracking logic.
- `ttylist`, `tty_count`, `ttylist_lock`: global list of allocated tty structures.
- `tk_cancc`, `tk_nin`, `tk_nout`, `tk_rawcc`: global tty statistics counters.
- Symbolic sleep strings such as `ttyin`, `ttyout`, `ttybg`, `ttopen`, and `ttclos`.

Open/close/lifecycle:
- `ttyopen()` initializes open state, device id, window size, and column state.
- `ttyclose()` detaches console redirection if needed, flushes queues, bumps `t_gen` so sleepers detect reuse/revoke, releases session references, and clears state.
- `ttymalloc()` allocates a tty and clists sized by baud rate, registers it in `ttylist`, and initializes restart timeout state.
- `ttyfree()` removes the tty from the global list, invalidates kqueue lists, frees queues, and frees the tty.

Input processing:
- `ttyinput()` handles receiver enable, pending reinput, stats, break/parity/framing errors, `PARMRK`, software/hardware flow control, stripping, literal-next, discard, signals, IXON start/stop, CR/LF translations, canonical editing, erase/kill/word erase/reprint/status, overflow behavior, canonical line completion, echo, and output restart.
- Canonical mode moves completed lines from raw queue to canonical queue.
- Noncanonical mode wakes readers directly and relies on `VMIN`/`VTIME` in `ttread()`.

Output processing:
- `ttyoutput()` handles `OPOST`, tab expansion, newline/carriage-return translation, uppercase/xcase mapping, `ONOEOT`, `ONOCR`, column accounting, and queue insertion.
- `ttwrite()` copies user data in chunks, fast-paths ordinary output runs, processes special output characters through `ttyoutput()`, mirrors console output to the console message buffer, sleeps on high-water output, and honors nonblocking mode.
- `ttstart()` invokes the device output routine when present.

Read behavior:
- `ttread()` enforces background read job control with `SIGTTIN`, processes pending input, implements canonical reads, noncanonical `VMIN`/`VTIME` timing, EOF handling, delayed suspend, user copyout via `ureadc()`, and unblocks input flow control after queue drain.

Generic ioctls:
- `ttioctl()` handles async mode, read counts, exclusive mode, flushing, virtual console redirection, drain, termios get/set, line discipline switching, start/stop, controlling terminal setup, foreground process group ownership, window size changes, timestamp control, and status output.
- Modifying ioctls enforce background job-control rules with `SIGTTOU`.
- `TIOCSETD` safely closes the old line discipline, opens the new one, and rolls back if open fails.

Flow control and wakeups:
- `ttyblock()` sends VSTOP and/or requests hardware input flow control when input queues exceed thresholds.
- `ttyunblock()` sends VSTART and/or clears hardware flow control when queues drain.
- `ttyflush()` drains read/write queues and wakes waiters/selectors.
- `ttwakeup()` and `ttwakeupwr()` notify readers, writers, selectors, and async recipients.

Kqueue and polling:
- `ttkqfilter()` attaches read, write, and poll-style except filters.
- Read filters report available input and carrier loss EOF/HUP.
- Write filters report output queue space and poll/select hangup.
- Except filters are restricted to poll-style hangup behavior.

Utility and stats:
- `ttyinfo()` prints load and foreground-process status for `^T`/`TIOCSTAT`.
- `ttysleep_nsec()` returns `ERESTART` if the tty generation changed while sleeping.
- `ttspeedtab()`, `ttsetwater()`, `ttychars()`, `tputchar()`, `ttycheckoutq()`, `ttywflush()`, and `ttywait()` support drivers and kernel tty writers.
- `sysctl_tty()` exposes counters and `KERN_TTY_INFO`; privileged callers see session pointers in exported tty stats.
- `ttytstamp()` records modem-signal transition timestamps when configured.

Filesystem/storage relevance:
- Not filesystem code. Important for character-device/VFS integration: tty device file operations rely on this line discipline for read/write/ioctl/poll semantics, controlling-terminal session state, revoke/restart behavior, and `/dev/console` access checks.
