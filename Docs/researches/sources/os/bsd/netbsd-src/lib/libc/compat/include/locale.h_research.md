# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/include/locale.h

Declares compatibility locale APIs.

It defines old `_LC_LAST` as `7`, declares `setlocale`, `__setlocale_mb_len_max_32`, and `compat_setlocale` renamed to `setlocale`.

This preserves older locale ABI, especially around multibyte locale evolution.
