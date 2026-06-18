# File Research: sources/os/bsd/netbsd-src/lib/libcurses/tstp.c

This file handles curses suspension/resume behavior, `SIGTSTP`, `SIGWINCH`, and saving/restoring terminal modes around `endwin()` and job-control stops.

Key entry points:
- `__stop_signal_handler()` blocks `SIGALRM`/`SIGWINCH`, calls `__stopwin()`, unblocks and sends `SIGTSTP`, then resumes with `__restartwin()`.
- `__set_stophandler()` and `__restore_stophandler()` install/restore the curses `SIGTSTP` handler.
- `__set_winchhandler()`, `__restore_winchhandler()`, and `__winch_signal_handler()` manage resize handling and KEY_RESIZE signaling.
- `__stopwin()` tears down curses terminal state.
- `__restartwin()` restores curses mode, resizes standard screens, restores colors/meta/cursor state, and refreshes `curscr`.
- `def_prog_mode()`, `reset_prog_mode()`, `def_shell_mode()`, and `reset_shell_mode()` implement curses terminal-mode save/restore APIs.

Important state and control flow:
- `tstp_set`, `winch_set`, `otstpfn`, and `owsa` track installed handlers and previous handlers.
- `__stopwin()` saves current terminal state into `save_termios`, restores old signal handlers, emits terminal exit sequences, flushes output, marks `endwin`, and restores `orig_termios`.
- `__restartwin()` checks `TIOCGWINSZ`, updates `LINES`/`COLS`, resizes `curscr` and `stdscr`, saves the new shell baseline, restores saved program terminal state, and restarts screen rendering.
- The resize handler either chains to a prior non-default handler or marks `_cursesi_screen->resized`.

Risks and notes:
- Signal handlers interact with global `_cursesi_screen`; correctness depends on screen initialization and async-signal assumptions inherited by curses.
- `__restore_winchhandler()` only restores if the current handler still matches the saved curses handler; otherwise it assumes the application has taken over.
- `TCSASOFT` is defaulted to `0` if absent, so hardware-setting preservation is platform-dependent.
