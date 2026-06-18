# File Research: sources/os/bsd/dragonflybsd/sys/kern/subr_prf.c

## Summary
Implements kernel printf/logging, message-buffer management, sysctl access to dmesg, pointer redaction, console/tty printing, and small formatting helpers.

## Main Responsibilities
- Provides `kprintf`, `kvprintf`, `log`, `uprintf`, `tprintf`, `ttyprintf`, `ksprintf`, `ksnprintf`, and allocated snprintf helpers.
- Implements `kvcprintf()` format parsing for integer, string, pointer, width, precision, length modifiers, `%n`, and BSD `%pb%i` bitfield formatting.
- Writes to console, controlling tty, and/or kernel message buffer through `kputchar()`.
- Maintains `msgbufp` ring buffer with `msgbufinit()`, `msglogchar()`, and `msgaddchar()`.
- Exposes `kern.msgbuf` and `kern.msgbuf_clear` sysctls.
- Runs `consttyd` to mirror message-buffer output to `constty`.
- Provides `hexdump()` and `kprint_cpuset()`.

## Important Behavior
Console output is serialized with a hard critical-section spinlock when possible, but may drop serialization to avoid nested hard-interrupt deadlocks. `security.ptr_restrict` can mask or replace `%p` output unless panicking, dumping, or in DDB. `security.unprivileged_read_msgbuf` controls whether non-root/non-wheel readers can access `kern.msgbuf`.

## Risks
Message-buffer updates are intentionally race-tolerant and can lose data on wrap or SMP races. `kvcprintf()` stops trusting the remaining format string after an unknown specifier because arguments may be misaligned. `kern.msgbuf` access control is security-sensitive because logs may contain kernel pointers or sensitive text.
