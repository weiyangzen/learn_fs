# File Research: sources/os/bsd/freebsd-src/sbin/hastd/pjdlog.c

Read completely: 613 lines.

This file implements HAST’s logging layer, supporting foreground stderr/stdout logging and daemon syslog logging, with debug filtering, prefixes, errno-aware messages, exit helpers, and assertion aborts.

Key responsibilities:
- Initializes and finalizes logging mode.
- Registers FreeBSD extended printf renderers for humanized numbers (`%N`) and socket addresses (`%S`), plus standard `%T` support.
- Maintains global log mode, debug level, and a bounded prefix string.
- Routes errors/warnings to stderr and informational/debug output to stdout in standard mode.
- Routes messages through `syslog()` in daemon mode.
- Preserves `errno` across logging setup and output routines.
- Provides `pjdlog_exit`, `pjdlog_exitx`, and `pjdlog_abort`.

Important interactions:
- Used by all HAST daemon modules for ordinary logging, debug traces, fatal exits, and assertions.
- The `%S` renderer is used by TCP address rendering in protocol code.

Reliability notes:
- Debug messages above the configured level are discarded early.
- Syslog messages are assembled into a 1024-byte buffer, so long messages are truncated by `snprintf`/`vsnprintf`.
- The implementation is process-global rather than thread-local; concurrent threads share prefix and debug mode.
