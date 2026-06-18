# File Research: sources/virtualization/guestfs-tools/gnulib/lib/error.c

Fallback implementation of GNU/glibc-style `error` and `error_at_line`, compiled only when `HAVE_ERROR_H` is absent.

Key behavior:
- Maintains `error_print_progname`, `error_message_count`, and `error_one_per_line`.
- Flushes stdout before printing errors.
- Prints program name from `getprogname`.
- Optionally appends system error text for `errnum`.
- Exits when `status` is nonzero.
- `error_at_line` can suppress duplicate file/line messages when `error_one_per_line` is set.
- Contains platform handling for Windows fd checks and strerror variants.

Research relevance: portability layer for consistent command-line diagnostics across platforms.
