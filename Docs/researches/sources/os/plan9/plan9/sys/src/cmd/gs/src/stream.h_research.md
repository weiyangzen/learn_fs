# File Research: sources/os/plan9/plan9/sys/src/cmd/gs/src/stream.h

Purpose: public stream API and exposed `stream` structure for performance-sensitive clients.

Key contents:
- Defines `stream_procs` virtual methods: `available`, `seek`, `reset`, `flush`, `close`, `process`, and `switch_mode`.
- Defines `struct stream_s`, including common stream state, buffer cursors, mode flags, position, procedures, filter link, interpreter bookkeeping, C `FILE *`, and file subrange state.
- Provides mode and validity macros (`s_mode_read`, `s_mode_write`, `s_can_seek`, etc.).
- Declares fast I/O macros and functions: `sgetc`, `spgetc`, `sputs`, `sputc`, `sgets`, `spskip`, inline cursor helpers, and buffer availability helpers.
- Declares allocation, initialization, string/file stream setup, subfile setup, filename access, filter setup, filter close, and null filter templates.

Dependencies: `scommon.h`, `srdline.h`, and `<stdio.h>` via users.

Integration notes: the struct is intentionally public so hot byte-level stream operations can be macros rather than procedure calls.

Risks: clients can directly touch internal fields; misuse can break cursor invariants documented in the header.
