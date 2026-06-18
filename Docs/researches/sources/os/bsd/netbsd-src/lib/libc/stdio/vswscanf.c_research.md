# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/vswscanf.c

Read completely: 119 lines.

Implements `vswscanf_l()` and `vswscanf()`. It converts the input wide string to a malloced multibyte string with `wcsrtombs_l()`, wraps that buffer in a read-only `FILE`, initializes wide I/O extension state, and delegates to `__vfwscanf_unlocked_l()`.

Allocation or conversion failure returns `EOF`. The file is another adapter around the shared stdio scanning engine, with an explicit comment noting the inefficient wide-to-multibyte-to-wide path.
