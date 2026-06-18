# File Research: sources/os/bsd/netbsd-src/lib/librumpuser/rumpuser_port.h

## Summary
Primary portability header for building librumpuser on NetBSD and non-NetBSD hosts.

## Key Details
- Embeds NetBSD-default configure results when `RUMPUSER_CONFIG` is not defined.
- Includes generated `rumpuser_config.h` when `RUMPUSER_CONFIG` is defined.
- Enables `_GNU_SOURCE` on Linux/GNU/glibc targets and adjusts FreeBSD visibility for C11 interfaces.
- Provides fallbacks for `MIN`, `MAX`, `getsubopt`, `clockid_t`, `clock_gettime`, `getenv_r`, `posix_memalign`, `aligned_alloc`, and numerous NetBSD-style compiler/utility macros.
- Supplies platform-specific atomic and type fixes for Android, Apple, Solaris file-offset handling, and NetBSD MIPS N32 `register_t`.
- Defines rumpuser lock alignment as `COHERENCY_UNIT` on NetBSD and `64` elsewhere.
- Normalizes socket constants, `MSG_NOSIGNAL`, `INFTIM`, sockaddr length setting, path/hostname limits, and `TIMEVAL_TO_TIMESPEC`.

## Notes
This header is the compatibility contract that lets the rest of librumpuser mostly use NetBSD-flavored APIs while compiling on POSIX-like hosts.
