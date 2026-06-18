# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/fparseln.c

Read completely: 249 lines.

This file implements `fparseln` when the host lacks a usable version. It reads logical lines, handles escaped comment characters, removes trailing newlines, processes line continuations, optionally unescapes selected escape sequences, tracks line numbers, and returns a newly allocated NUL-terminated buffer.

Important interactions: uses `fgetln` or `__fgetstr` depending on reentrant/tool build configuration.

Security/reliability notes: allocation failures free partial buffers and return `NULL`; callers own the returned buffer. Escape handling is byte-oriented and controlled by caller-supplied `str[3]` and flags.
