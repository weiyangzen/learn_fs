# sources/user-network-fs/libfuse/lib/fuse_signals.c

Purpose: `fuse_signals.c` installs and removes process-wide signal handlers that tell a FUSE session to exit on normal teardown signals, ignore SIGPIPE, and optionally abort with a backtrace on fatal signals.

Important APIs, types, and functions: Public functions are `fuse_set_signal_handlers`, `fuse_set_fail_signal_handlers`, and `fuse_remove_signal_handlers`. Internal helpers include `exit_handler`, `exit_backtrace`, `do_nothing`, `dump_stack`, `set_one_signal_handler`, `_fuse_set_signal_handlers`, and `_fuse_remove_signal_handlers`. Static arrays define teardown signals (`SIGHUP`, `SIGINT`, `SIGTERM`), ignored signals (`SIGPIPE`), and fatal backtrace signals (`SIGILL`, `SIGTRAP`, `SIGABRT`, `SIGBUS`, `SIGFPE`, `SIGSEGV`).

Control flow: Installing handlers walks the selected signal arrays and only replaces default handlers, preserving handlers set by the application. Teardown signals call `fuse_session_exit` and store the signal number in `se->error`. Fatal handlers exit the session, remove handlers, log the signal, dump a backtrace when available, and abort. Removal resets handlers back to default only if they still match the libfuse-installed handler and clears the global `fuse_instance` if it matches the supplied session.

State and persistence behavior: The file uses one process-global `static struct fuse_session *fuse_instance`, so the last installed session owns signal handling. There is no per-session handler table. Backtrace storage is a static buffer when enabled.

Dependencies and integration points: It depends on `fuse_lowlevel.h` and `fuse_i.h` for session access and logging, POSIX `sigaction`, and optional `execinfo` backtrace APIs. `helper.c` installs these handlers before entering single-threaded or multithreaded loops.

Risks: Signal handlers call functions that are not strictly async-signal-safe, which is common in libfuse but still a robustness risk. The global session pointer is awkward for multiple simultaneous sessions. Handler removal can log "unknown session" if sessions are removed out of order. `SIGCANCEL` is intentionally avoided because FUSE worker threads use cancellation-like wakeups around blocking reads.

Test signals: Tests should verify handler install/remove idempotence, preservation of pre-existing non-default handlers, SIGPIPE ignoring, `fuse_session_exit` on teardown signals, failure-signal abort behavior under backtrace-enabled builds, and multi-session ordering warnings.
