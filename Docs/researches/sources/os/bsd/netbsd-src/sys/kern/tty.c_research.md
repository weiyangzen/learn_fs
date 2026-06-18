# File Research: sources/os/bsd/netbsd-src/sys/kern/tty.c

## Purpose

`tty.c` is NetBSD's main terminal subsystem implementation. It handles terminal lifecycle, termios processing, input canonicalization, output processing, ioctls, read/write paths, job control, flow control, poll/kqueue support, tty allocation, controlling terminal state, and deferred tty-generated signal delivery.

## Main Responsibilities

- Provides global tty locking, tty lists, queue sizing, and subsystem initialization.
- Implements default terminal line discipline operations used by `tty_conf.c`.
- Processes input characters with termios rules, erase/kill/reprint/status controls, software flow control, canonical/noncanonical buffering, echoing, and signal generation.
- Processes output with termios output transformations, queueing, high/low water marks, and device start callbacks.
- Implements common tty ioctls for termios, line discipline changes, process groups, controlling terminal setup, console redirection, queue sizing, window size, and pty pass-through commands.
- Implements `ttread`, `ttwrite`, `ttpoll`, `ttykqfilter`, `ttywait`, `ttyflush`, and modem-carrier handling.
- Manages tty references used by `constty` and close/revoke synchronization.
- Defers tty-originated signal delivery through a soft interrupt.

## Core Data Model

Each `struct tty` owns raw, canonical, and output clists, termios flags/control characters, process/session pointers, condition variables, select/kqueue state, output callbacks, and deferred signal sets.

The subsystem uses a single global spin mutex `tty_lock` for tty state. `proc_lock` protects process group/session interactions. `constty_lock` plus pserialize and `t_refcnt` protect the special console tty reference path.

## Input and Read Path

`ttyinput_wlock()` handles break/parity/framing conditions, IXOFF and hardware input flow control, literal-next, discard, signals, IXON start/stop, CR/NL translation, canonical erase/kill/word erase/reprint/status handling, buffer overflow policy, line delimiter detection, and echoing.

`ttread()` enforces background read job-control rules, handles canonical reads from `t_canq`, noncanonical `VMIN`/`VTIME` behavior, delayed suspend, EOF processing, user copying, and unblocking of software/hardware input flow control as queues drain.

## Output and Write Path

`ttyoutput()` performs output post-processing including tab expansion, ONLCR/OCRNL/ONOCR/ONLRET handling, CEOT suppression, column accounting, and queue insertion.

`ttwrite()` enforces carrier and background write rules, fetches user data in chunks, fast-paths ordinary output with `b_to_q`, sends special characters through `ttyoutput`, starts device output, and sleeps when the output queue is above the high-water mark.

## Ioctl and Job Control

`ttioctl()` provides shared tty ioctl handling after line-discipline-specific logic. It implements termios get/set, discipline switching, process-group/session queries and updates, `TIOCSCTTY`, `TIOCSTI` authorization, `TIOCCONS`, queue flush/drain, queue size changes, `TIOCSTAT`, window-size changes, and compatibility/module hooks.

Foreground/background checks use `isbackground`, process group state, and `SIGTTIN`/`SIGTTOU`. `ttysig()` queues terminal-generated signals for later delivery to the foreground process group, async I/O process group, or session leader.

## Initialization and Lifetime

`tty_alloc()` allocates the tty, clists, condition variables, callout, line-discipline reference, and select state. `tty_attach()`/`tty_detach()` maintain the global tty list. `ttyclose()` removes console status, flushes queues, bumps the generation number, clears session/process group state, waits for references to drain, and releases the session reference.

`tty_init()` initializes locks, pserialize, condition variables, softint signal handling, a kauth listener for exclusive opens, and `kern.tkstat` / `kern.tty.qsize` sysctls.
