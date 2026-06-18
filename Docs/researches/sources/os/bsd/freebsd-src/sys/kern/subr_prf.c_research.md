# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_prf.c

## Purpose
Implements kernel formatted output, logging integration, message-buffer initialization/sysctls, hexdump utilities, and sbuf drains. This is the central `printf`/`log` formatting path for FreeBSD kernel code.

## Main Interfaces
Output/logging:
- `printf()`, `vprintf()`, `log()`, `vlog()`, `uprintf()`, `tprintf()`, `vtprintf()`.
- `log_console()`: copies console output into the message log.
- Internal `_vprintf()`, `putchar()`, `prf_putchar()`, `prf_putbuf()`.

Formatting:
- `sprintf()`, `vsprintf()`, `snprintf()`, `vsnprintf()`, `vsnrprintf()`.
- `kvprintf()`: scaled-down kernel formatter.
- `ksprintn()`: numeric conversion helper.

Message buffer:
- `msgbufinit()`.
- Sysctls `kern.msgbuf` and `kern.msgbuf_clear`.
- DDB `show msgbuf`.

Diagnostics:
- `hexdump()`, `sbuf_hexdump()`.
- `counted_warning()`.
- `sbuf_putbuf()`, `sbuf_printf_drain()`, DDB sbuf drain.

## Implementation Notes
Output flags route formatted characters to console, tty, and/or log. Console/log output may be buffered when `PRINTF_BUFR_SIZE` is defined. `vlog()` writes to log and only falls back to console when no log reader is open. `vprintf()` writes to console and log, then triggers message-buffer wakeups unless panicked.

`kvprintf()` supports common integer/string/char/pointer formats plus kernel-specific `%b` bitfield decoding and `%D` hexdump formatting. Kernel `%n` is intentionally unsupported, but consumes the pointer argument to keep argument walking aligned. Unknown formats are emitted literally and stop further conversion because argument alignment is no longer trustworthy.

`msgbufinit()` places `struct msgbuf` at the end of the supplied memory, attempts to preserve old contents across remap/reinit, fetches `kern.boot_tag` on first mapping, and prints a boot tag if configured.

`kern.msgbuf` requires `PRIV_MSGBUF`, peeks the entire buffer without consuming it, skips the first incomplete line after wrap, and appends a NUL terminator. `kern.msgbuf_clear` clears under `msgbuf_lock`.

## Dependencies
Uses console, tty, msgbuf, syslog priorities, proc/session locks, sysctl privilege checks, DDB, sbuf, tslog, and kernel panic/KDB state.

## Research Notes
This file is foundational for observing all filesystem and storage code. Its locking and context behavior matter because logging can be called from interrupts, panic paths, and early boot.
