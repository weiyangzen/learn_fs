# File Research: sources/os/bsd/freebsd-src/sbin/dmesg/dmesg.c

## Purpose
Implements the `dmesg` utility for printing the kernel message buffer from the running kernel or a kernel core file, with optional clearing and timestamp conversion.

## Main Elements
- Options:
  - `-a`: include non-kernel syslog facility messages.
  - `-c`: clear running kernel message buffer after reading.
  - `-t`: convert relative bracketed timestamps using boot time.
  - `-f`: timestamp output format for `strftime`.
  - `-M`/`-N`: read message buffer from core and namelist through `libkvm`.
- Running-kernel path: uses `sysctlbyname("kern.msgbuf")`, allocates growth slack, strips trailing NUL, optionally clears via `kern.msgbuf_clear`.
- Core-file path: uses `kvm_open`, `kvm_nlist` for `_msgbufp`, validates `MSG_MAGIC`, unwraps circular `msgbuf`.
- Output path: ensures newline/NUL termination, strips leading NULs, splits lines, filters syslog priority prefixes, escapes with `strvisx`, and optionally converts `[seconds.frac]` to absolute local time.
- `usage()`: prints CLI syntax.

## Dependencies And Integration
Uses kernel `msgbuf` layout, sysctl, `libkvm`, syslog priority macros, locale/vis escaping, and boot-time sysctl.

## Risk Notes
Core reading depends on matching kernel symbol/layout. Timestamp conversion is best-effort and falls back to original text if parsing fails.
