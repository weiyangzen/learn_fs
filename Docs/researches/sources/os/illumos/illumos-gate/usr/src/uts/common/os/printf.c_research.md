# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/printf.c

## Purpose

`printf.c` implements core kernel formatted output and logging wrappers: `printf`, `uprintf`, `cmn_err`, `dev_err`, STREAMS `strlog`, assertion failure reporting, zone-aware output, syslog delivery, console delivery, interrupt-safe logging, and optional panic-buffer logging.

Read completely: 367 lines.

## Main Responsibilities

- Formats kernel log messages with message IDs, module names, prefixes, suffixes, device instance prefixes, and syslog metadata.
- Routes messages to console, global/local zone logs, user tty, interrupt queues, or panic buffer depending on flags and context.
- Provides public wrappers for global and zone-specific printf/cmn_err variants.
- Implements user-visible `uprintf()` behavior for current tty plus zone logging.
- Converts `CE_*` severities to syslog levels and panic behavior.
- Implements assertion failure handlers `assfail()` and `assfail3()`.
- Provides STREAMS logging entry points `strlog()` and `vstrlog()`.

## Important Data Structures And Globals

- `panicbuf_log`, `panicbuf_index`: controls optional circular logging into `panicbuf`.
- `aask`, `aok`: assertion debug/panic behavior knobs.
- `ce_to_sl`, `ce_prefix`, `ce_suffix`: maps `CE_*` severities to log flags and message decoration.
- `log_global`, `log_intrq`: external logging subsystem state used by `cprintf()`.

## Control Flow And Algorithms

`cprintf()` is the common formatter and dispatcher. It detects interrupt context, computes a stable message ID from the format string, handles leading control characters (`^`, `!`, `?`), formats the message into a stack buffer or a larger temporary buffer, sends console-only messages directly when appropriate, builds log messages with `log_makemsg()`, optionally writes to the user's controlling tty, and either queues interrupt-context messages for softcall flushing or calls `log_sendmsg()` directly.

`vuprintf()` sends one message to the user tty and global-zone syslog, then sends a separate local-zone syslog message when the caller is not in the global zone.

`vzdcmn_err()` panics for `CE_PANIC`, otherwise maps valid severities to `cprintf()`. `assfail()` and `assfail3()` optionally enter the debugger, then panic unless assertions are allowed or a panic is already in progress.

## Dependencies And Integration

- Uses logging/STREAMS message APIs (`log_makemsg`, `log_sendmsg`, `putq`, `softcall`).
- Uses console, panic, module, DDI device, vnode, session, and zone interfaces.
- Assertion paths integrate with `debug_enter()` and `panic()`.

## Locking And Concurrency

The code avoids unsafe user/tty logging while holding `pidlock` or running in interrupt context, falling back to console/global logging. Panic buffer updates use `atomic_cas_32()` on `panicbuf_index`. Larger message allocation is avoided in interrupt context.

## Notable Risks And Invariants

- `va_list` reuse is handled explicitly in `vuprintf()` with `va_copy()`.
- Interrupt-context messages cannot sleep and are delivered through `log_intrq`.
- Long messages may be dynamically allocated only outside interrupt context.
- Local-zone output is disallowed from interrupt context by assertion.
- Leading format control characters alter routing before formatting.

## Research Relevance

This file defines how kernel diagnostics from filesystem, STREAMS, drivers, and resource-control paths reach console and logs. Understanding its context restrictions is important when interpreting logging behavior from low-level storage paths.
