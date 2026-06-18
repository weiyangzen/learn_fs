# File Research: sources/os/bsd/netbsd-src/lib/libc/arch/m68k/string/memccpy.S

This assembly file implements `memccpy`. It copies bytes from source to destination until the requested count is exhausted or the terminator byte is copied, returning the destination pointer just past the copied terminator or `NULL` if no terminator is found.

It has separate paths for NUL and non-NUL terminators, uses `%d2` as a saved scratch register in the non-NUL path, and has ColdFire-specific loop handling where `dbcc` is unavailable or unsuitable. ABI-sensitive return handling includes an `__SVR4_ABI__` path that mirrors the pointer return into `%a0`.
