# File Research: sources/os/bsd/freebsd-src/sys/kern/tty_ttydisc.c

## Purpose
Implements the standard termios TTY line discipline: canonical/raw reads, VMIN/VTIME semantics, output post-processing, input processing, echoing, erase/kill/word erase/reprint, signal generation, software flow control, bypass mode, hooks, and driver-facing getc/rint paths.

## Main State and Macros
- Counters: `kern.tty_nin` and `kern.tty_nout`.
- Termios helper macros compare control characters and flag fields.
- Control-character helpers classify tabs/newlines/control bytes/UTF-8 continuation bytes.
- Uses stack buffers for chunked input/output and UTF-8 erase handling.

## Read Path
- `ttydisc_read()` dispatches to canonical or raw implementations.
- Canonical reads use `ttyinq_findchar()` to stop at newline/VEOL/VEOF and trim VEOF from userspace output.
- Raw reads implement POSIX cases:
  - no timer (`VTIME == 0`),
  - read timer (`VMIN == 0`, `VTIME != 0`),
  - interbyte timer (`VMIN != 0`, `VTIME != 0`).
- Background reads call `tty_wait_background()` with `SIGTTIN`.
- After reading, input high-water state is cleared when enough space is available.

## Write Path
- `ttydisc_write()` chunks user data, applies `OPOST` processing, handles `FLUSHO`, writes into `ttyoutq`, sleeps on output high water unless nonblocking, and wakes the driver.
- `ttydisc_write_oproc()` handles `ONOEOT`, backspace column correction, tab expansion, newline-to-CRLF, CR-to-NL, `ONOCR`, `ONLRET`, and column/write-position maintenance.

## Input Path
- `ttydisc_rint()` processes received characters:
  - break/framing/parity handling with `IGNBRK`, `BRKINT`, `IGNPAR`, `PARMRK`;
  - `IXANY`, `ISTRIP`, literal-next;
  - discard/flush-output;
  - `VINTR`, `VQUIT`, `VSUSP`, `VSTATUS` signal generation;
  - `IXON` start/stop handling;
  - CR/NL conversion;
  - canonical erase, kill, word erase, and reprint.
- Accepted bytes are written to `ttyinq`; raw mode canonicalizes every byte, canonical mode canonicalizes on unquoted line delimiters.
- `ttydisc_rint_simple()` uses bypass mode when available; otherwise loops through `ttydisc_rint()`.
- `ttydisc_rint_bypass()` writes directly to input queue and canonicalizes all bytes for fast raw-like paths.
- `ttydisc_rint_done()` wakes readers and driver output for echo.

## Echo and Editing
- `ttydisc_echo_force()` renders control characters, `^X` notation, EOF backspacing, and normal echo.
- `ttydisc_rubchar()` removes the last canonical input byte, including quoted/control characters, tabs, and UTF-8 sequences using `teken` width helpers.
- `ttydisc_rubword()` implements word erase with optional `ALTWERASE`.
- `ttydisc_reprint()` reprints the current canonical line after `VREPRINT` or display disruption.

## Driver Output Side
- `ttydisc_getc()` drains output queue into a kernel buffer unless stopped and supports hooks for injection/capture.
- `ttydisc_getc_uio()` copies output to userspace, using direct queue UIO reads unless hooks require a shadow buffer.
- `ttydisc_getc_poll()` reports available output.
- `ttydisc_wakeup_watermark()` clears output high-water state when enough space is available.
- `tty_putstrn()` writes kernel strings through echo/output processing and wakes the driver.

## Hooks and Modem State
- `ttydisc_optimize()` enables `TF_BYPASS` when hooks or termios flags allow fast input.
- `ttydisc_modem()` handles carrier changes, wakes open waiters, enters zombie state on carrier loss, sends SIGHUP, and flushes queues.

## Dependencies
Depends on `tty_inq.c`, `tty_outq.c`, tty core locking/wakeup/signal helpers, `teken` UTF-8 width conversion, vnode/uio APIs, and tty hooks.

## Notes and Risks
- This is the behavioral center of terminal semantics; small flag interactions can change POSIX-visible behavior.
- UTF-8 erase logic must carefully restore input bytes when malformed sequences are detected.
- Bypass mode improves throughput but must be disabled when termios flags or hooks require per-character processing.
