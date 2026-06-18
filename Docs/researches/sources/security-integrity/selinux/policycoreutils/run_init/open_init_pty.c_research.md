<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/run_init/open_init_pty.c -->
# sources/security-integrity/selinux/policycoreutils/run_init/open_init_pty.c

## Purpose
Wraps a command in a freshly allocated pseudo-terminal so the spawned init command receives a PTY with the desired SELinux labeling path instead of reusing the caller's PTY.

## Important APIs, Types, And Functions
Important helpers are `tty_semi_raw()`, `tty_atexit()`, the `struct ring_buffer` routines (`rb_init`, `rb_space`, `rb_chunk_size`, `rb_read`, `rb_write`), `setfd_nonblock()`, `setfd_block()`, `setfd_atexit()`, and `sigchld_handler()`. It uses `forkpty`, `termios`, `ioctl(TIOCGWINSZ)`, `select`, nonblocking `read`/`write`, `waitpid`, and `execvp`.

## Control Flow
`main()` validates a program argument, installs a SIGCHLD handler so blocking I/O can be interrupted, captures terminal attributes/window size for interactive sessions, then calls `forkpty()`. The child disables echo/newline output translation and execs the requested program. The parent switches the pty, stdin, and stdout to nonblocking mode, optionally puts the terminal into semi-raw mode, then repeatedly uses `select()` to shuttle data between stdin/stdout and the pty through two ring buffers until the child exits and buffered data drains or retry limits are reached.

## State And Persistence
It temporarily changes terminal modes and file descriptor blocking flags, restoring them through `atexit` handlers. No persistent filesystem state is written.

## Dependencies And Integration Points
It is called by `run_init` after `setexeccon()` so the PTY allocation happens in the init execution context. It depends on libc, libutil/pty support, and terminal-capable stdio.

## Risks And Edge Cases
I/O retry handling treats repeated nonpositive reads/writes as terminal failure. Noninteractive use omits inherited termios/window sizing. Exit status is propagated only when `waitpid` records normal or signal termination.

## Test Signals
Tests should verify interactive echo behavior, stdin/stdout relay, child exit status propagation, noninteractive execution, SIGCHLD interruption, terminal restoration after early failures, and large bidirectional streams exceeding the 2 KiB buffers.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/policycoreutils/run_init/open_init_pty.c -->
