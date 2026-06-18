# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/vswprintf.c

Read completely: 113 lines.

Implements `vswprintf_l()` and `vswprintf()`. It formats wide output through `__vfwprintf_unlocked_l()` into a dynamically allocated multibyte string-backed `FILE`, then converts that multibyte result back into the caller's wide-character buffer with `mbsrtowcs_l()`.

It rejects `n == 0` with `EINVAL`, returns `ENOMEM` on allocation failure, preserves `errno` across formatting failure cleanup, and reports `EOVERFLOW` if the converted wide output would fill all `n` slots. The source comments call out the inefficient round-trip: wide formatting converts to multibyte, then this wrapper converts back to wide.
