# File Research: sources/os/bsd/netbsd-src/lib/libc/regex/regsub.c

Implements replacement expansion helpers `regnsub()` and `regasub()`. The shared `regsub1()` expands `&` as match 0 and `\digit` as submatch references, while allowing escaped `\\` and `\&`.

The internal `struct str` supports either fixed caller buffers or dynamically allocated buffers. If fixed space is insufficient, it still counts required length but omits writes. `regasub()` allocates and grows the output buffer in `REINCR` chunks.

Return value is the expanded length excluding the terminating NUL; `-1` signals allocation or fixed-buffer failure conditions.
