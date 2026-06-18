# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_prf.c

## Purpose
Implements NetBSD kernel printing, logging, panic reporting, autoconfiguration print helpers, DDB printing, tty/user printing helpers, `snprintf`/`vasprintf`, and the kernel `kprintf` formatter.

## Main Entry Points
- Initialization and locking: `kprintf_init()`, `kprintf_lock()`, and `kprintf_unlock()`.
- Panic/logging: `panic()`, `vpanic()`, `log()`, `vlog()`, `logpri()`, `klogpri()`, `addlog()`, and `tablefull()`.
- Console/TTY APIs: `printf()`, `vprintf()`, `printf_flags()`, `vprintf_flags()`, `printf_tolog()`, `printf_nolog()`, `printf_nostamp()`, `uprintf()`, `uprintf_locked()`, `tprintf_open()`, `tprintf()`, `tprintf_close()`, `ttyprintf()`, and `device_printf()`.
- Autoconfiguration helpers: `aprint_normal*`, `aprint_error*`, `aprint_naive*`, `aprint_verbose*`, `aprint_debug*`, and `aprint_get_error_count()`.
- Formatting APIs: `snprintf()`, `vsnprintf()`, `vasprintf()`, and `kprintf()`.

## Control Flow And State
`kprintf_mtx` serializes console/log/buffer output after early bootstrap. `putchar()` handles timestamp insertion, syslog priority markers, DDB output, entropy collection for `RND_PRINTF`, and dispatches to `putone()`. `putone()` sends characters to the controlling tty, log buffer, or virtual console; it enters pserialize read sections around `constty` access and clears `constty` during panic.

`vpanic()` stops SPL debugging, elects the first panic CPU with atomic CAS, binds/offlines scheduling state to keep other CPUs out, formats and records `panicstr`, optionally enters KGDB/DDB, and reboots with dump flags depending on `dumponpanic` and recursive shutdown state.

`kprintf()` is a compact integer/string formatter supporting flags, width, precision, length modifiers, bases, pointers, and strings. `%n` is intentionally consumed but produces no output. `vsnprintf()` uses `TOBUFONLY` and then NUL-terminates according to returned length.

## Dependencies
Touches console drivers, msgbuf/log wakeups, tty/session/proc state, pserialize, device and ifnet naming, boot flags, DDB/KGDB, reboot/dump policy, syslog priorities, random source collection, and kmem for `vasprintf`.

## Risks And Notes
Printing is used in panic and interrupt-adjacent paths, so recursion and locking order matter. Some user/tty print helpers intentionally avoid the global kprintf mutex when writing only to a tty. Timestamp precision is clamped to 0-9. The formatter is not full libc `printf`; unsupported/unsafe features such as `%n` are suppressed, and floating point is not implemented despite internal flag names.
