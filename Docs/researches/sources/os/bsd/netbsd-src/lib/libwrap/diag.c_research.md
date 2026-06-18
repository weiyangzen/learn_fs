# File Research: sources/os/bsd/netbsd-src/lib/libwrap/diag.c

## Purpose
Central diagnostic logging for `libwrap`.

## Key Details
- Defines global `tcpd_context` and `tcpd_buf`.
- `tcpd_warn` logs warning diagnostics and continues.
- `tcpd_jump` logs an error and `longjmp`s with `AC_ERROR`.
- `tcpd_diag` expands `%m` using `expandm`, then logs with file/line context when available.

## Dependencies and Role
- Error-reporting backbone for access table parsing and matching.
