# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/vsscanf.c

Read completely: 89 lines.

Implements `vsscanf_l()` and `vsscanf()`. It wraps the input string in a read-only string-backed `FILE`, sets `_r` and `_bf._size` from `strlen(str)`, installs an `eofread()` callback that always returns 0, and delegates parsing to `__svfscanf_unlocked_l()`.

The implementation is a thin adapter from string input to the stdio scanning engine. It asserts non-null `str` and `fmt`, and ordinary `vsscanf()` uses `_current_locale()`.
