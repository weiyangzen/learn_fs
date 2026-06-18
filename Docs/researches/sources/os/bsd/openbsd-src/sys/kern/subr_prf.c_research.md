# File Research: sources/os/bsd/openbsd-src/sys/kern/subr_prf.c

Implements kernel printf, logging, panic printing, assertion failure reporting, terminal-directed output, DDB printing hooks, `snprintf()`/`vsnprintf()`, and small compiler helper wrappers for `puts()`/`putchar()`.

Output routing is controlled by internal flags: console, controlling tty, kernel message buffer, buffer-only formatting, DDB, and count-only formatting. `kputchar()` is the common character sink, routing to `constty`, `msgbuf_putchar()`, `v_putc`, or `db_putchar()` depending on flags and debugger/panic state.

`panic()` records the first panic message in the current CPU’s panic buffer using `atomic_cas_ptr()` on `panicstr`, disables SPL assertions, forces console printing under quiet boot, prints through DDB-aware panic functions, enters DDB or dumps a stack when configured, then calls `reboot()` with dump/autoboot flags and `RB_NOSYNC` on recursive panic.

Logging functions include `log()`, `logpri()`, and `addlog()`. They write priority-prefixed messages to the kernel log buffer at high SPL, mirror to console when `/dev/klog` is not open, and wake log readers. `printf()` and `vprintf()` use `kprintf_mutex` for console/log serialization and wake log readers unless already panicking.

TTY-specific paths include `uprintf()` for the current process controlling tty, NFS-gated `tprintf_open()`/`tprintf()`/`tprintf_close()` for process-targeted messages with session references, and `ttyprintf()` for direct tty output.

`kprintf()` is a compact kernel formatter derived from BSD libc formatting. It supports common integer, string, char, pointer, width, precision, flags, `h/l/ll/q/z` modifiers, and OpenBSD/BSD `%b` bitfield decoding. It explicitly panics on `%n`. Buffer formatting uses a tail pointer to enforce `snprintf()` truncation semantics while still counting produced characters.

DDB integration provides `db_printf()`/`db_vprintf()` and panic-time preference for debugger output. `splassert_fail()` reports IPL mismatches and, depending on `splassert_ctl`, ignores, dumps stack, enters DDB, or panics.

Filesystem relevance: not filesystem-specific, but heavily used by VFS, device, and storage code for diagnostics, panic reporting, mount/buffer warnings, and DDB inspection. The formatter and log behavior define what can safely be printed from interrupt, panic, or normal kernel contexts.
