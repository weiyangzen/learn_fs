# File Research: sources/os/bsd/freebsd-src/sbin/hastd/pjdlog.h

Read completely: 117 lines.

This header declares the logging API and convenience macros used throughout HAST.

Key responsibilities:
- Defines standard and syslog logging modes.
- Declares initialization, finalization, mode, debug-level, and prefix functions.
- Declares common, regular, debug, errno-aware, exit, exitx, and abort logging functions.
- Provides log-level convenience macros such as `pjdlog_error`, `pjdlog_warning`, and `pjdlog_info`.
- Provides verification/assertion macros: `PJDLOG_VERIFY`, `PJDLOG_RVERIFY`, `PJDLOG_ABORT`, `PJDLOG_ASSERT`, and `PJDLOG_RASSERT`.

Important interactions:
- The macros are used as hard invariants throughout protocol, worker, parser, and metadata code.
- `NDEBUG` disables `PJDLOG_ASSERT`/`PJDLOG_RASSERT` but not `PJDLOG_VERIFY`.

Reliability notes:
- Fatal helpers are annotated `__dead2`; formatted APIs are annotated `__printflike`.
