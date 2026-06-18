# File Research: sources/os/bsd/netbsd-src/lib/libc/compat/locale/compat_setlocale32.c

Read completely: 61 lines.

This implements `__setlocale_mb_len_max_32`, the compatibility locale wrapper for old platforms where `MB_LEN_MAX` was effectively 32. It sets `__mb_len_max_runtime` to `32` and delegates to `__setlocale`.

Important interactions: hppa is explicitly excluded because it used a different historical maximum and has an architecture-specific file.

Security/reliability notes: no direct input handling beyond forwarding the locale string. ABI correctness depends on selecting the right per-architecture variant.
