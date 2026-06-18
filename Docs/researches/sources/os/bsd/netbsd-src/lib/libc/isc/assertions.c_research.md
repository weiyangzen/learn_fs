# File Research: sources/os/bsd/netbsd-src/lib/libc/isc/assertions.c

Implementation of the ISC assertion callback mechanism.

Exports:
- Global `assertion_failure_callback __assertion_failed`, defaulting to `default_assertion_failed`.
- `set_assertion_failure_callback`.
- `assertion_type_to_text`.

Default failure behavior:
- Prints `file:line: TYPE(condition)` to stderr.
- Appends `strerror(errno)` for `_ERR` assertion forms.
- Calls `abort()`.

Used by assertion macros in `isc/assertions.h`.
