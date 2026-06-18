# File Research: sources/os/bsd/netbsd-src/lib/libc/stdio/vsnprintf_ss.c

Read completely: 506 lines.

Implements `vsnprintf_ss()`, a small, self-contained `printf(3)` formatter for bounded string output. It parses flags, width, precision, integer length modifiers, `%c`, `%s`, signed/unsigned integer formats, `%p`, `%n`, and unknown conversions, but intentionally omits floating-point support despite keeping some inherited flag names.

Output is written through a `PUTCHAR` macro that advances only while inside the caller's buffer, while `ret` tracks the full formatted length that would have been produced. It rejects `slen > INT_MAX` with `EOVERFLOW`, supports `slen == 0`, and always NUL-terminates when possible.

Important behavior: integer formatting uses a local 128-byte conversion buffer and manual base conversion. `%s` with precision uses `memchr()` to avoid reading beyond the precision limit. The final `sbuf == tailp` case writes `sbuf[-1] = '\0'`, which is safe only when `slen > 0`; when `slen == 0`, `tailp == sbuf`, so this path relies on callers not passing a zero-length writable buffer despite the diagnostic allowing it.
