# File Research: sources/os/bsd/netbsd-src/lib/libc/stdlib/strsuftoll.c

Implements `strsuftoll()` and `strsuftollx()` for parsing positive decimal size expressions with suffix multipliers. Supported suffixes include `b` for 512-byte blocks, `k`, `m`, `g`, `t`, and `w` for `sizeof(int)`, plus multiplicative expressions separated by `x` or `*`.

`strsuftoll()` exits with `errx()` on error; `strsuftollx()` writes an error message into the caller buffer and returns zero. The parser checks `strtoll` overflow, multiplication wrap, min/max bounds, invalid trailing text, and caps recursive product parsing at depth 16.
