# File Research: sources/os/bsd/netbsd-src/sys/sys/dkstat.h

Very small header exposing historical disk/terminal I/O counters to kernel code.

Key content:
- Under `_KERNEL`, declares `tk_cancc`, `tk_nin`, `tk_nout`, and `tk_rawcc` as `uint64_t`.

Important behavior:
- No user-visible declarations beyond the guard.
- Legacy statistics plumbing.
