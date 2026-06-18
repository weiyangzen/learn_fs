# File Research: sources/os/plan9/plan9/sys/src/cmd/aux/listen.c

This file implements Plan 9's service listener supervisor.

Key behavior:
- Scans service directories for files named with the selected protocol prefix.
- Announces network addresses derived from service filenames.
- Accepts incoming calls and execs matching service programs.
- Supports trusted and untrusted service directories; untrusted listeners become user `none` and enter a new namespace.
- Periodically rescans service directories unless immutable mode is requested.

Important details:
- Disabled services are represented by missing or zero-length service files.
- Rejects service names containing `/`, beginning with `.`, or too long.
- Binds connection data to `/dev/cons` and dup's it to fd 0, 1, and 2 before exec.
- Logs service starts, calls, and errors to `listen`.
- Handles address-in-use failures without repeated noisy logs.

Filesystem relevance:
- Direct to Plan 9 service namespace conventions: discovers executable service files and uses network control/data files.
