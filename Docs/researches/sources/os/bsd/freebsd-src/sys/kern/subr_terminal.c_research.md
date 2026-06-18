# File Research: sources/os/bsd/freebsd-src/sys/kern/subr_terminal.c

## Purpose
Bridges terminal emulator state, TTY devices, and console devices. It wraps the `teken` terminal emulator with a `struct terminal` interface and exposes both ttydevsw and consdev operations.

## Terminal Allocation and Setup
- `terminal_alloc()` allocates and initializes a terminal, sets terminal class callbacks and driver softc.
- `terminal_init()` initializes console spin locking when needed, initializes `teken`, reads `teken.fg_color`/`teken.bg_color` tunables, adjusts default/kernel attributes, and sets default emulator attributes.
- `terminal_maketty()` allocates and publishes a TTY device using formatted terminal name.
- `terminal_set_winsize_blank()` updates terminal and teken dimensions, optionally blanks the display, calls driver fill, and syncs TTY window size.
- `terminal_set_winsize()` is the default blanking resize wrapper.
- `terminal_set_cursor()` forwards cursor updates to teken.
- `terminal_mute()` suppresses terminal input/rendering temporarily.

## Input Paths
- `terminal_input_char()` converts terminal characters to UTF-8 and injects into TTY discipline, ignoring the right half of CJK full-width characters.
- `terminal_input_raw()` injects one raw byte into TTY discipline.
- `terminal_input_special()` asks teken for a key sequence and injects it into the TTY.

## TTY Binding
The `terminal_tty_class` operations:
- `termtty_open()` and `termtty_close()` notify driver `tc_opened`.
- `termtty_outwakeup()` drains TTY output into teken, calls `tc_done()`, and rings the bell if teken requested it.
- `termtty_ioctl()` handles `CONS_GETINFO` locally, forwards other ioctls to the terminal class while temporarily dropping the TTY lock, and resets cursor after `CONS_CLRHIST`.
- `termtty_mmap()` forwards mmap requests to the terminal class.

## Console Binding
- `termcn_cnregister()` allocates or reuses a `consdev`, marks the terminal as console, initializes console mode, and registers with `cnadd()`.
- `termcn_cnprobe()` initializes and delegates console probing.
- `termcn_cngetc()` and `termcn_cnputc()` call terminal-class console get/put operations.
- `termcn_cnputc()` temporarily applies kernel-message attributes while feeding a byte to teken.
- `termcn_cngrab()`/`termcn_cnungrab()` delegate debugger/console grab transitions.

## Teken Callbacks
`termteken_*` functions translate emulator events to terminal-class methods:
- bell, cursor, putchar, fill, copy, pre/post input, parameter changes.
- `termteken_respond()` is disabled because injecting emulator responses can cause lock and feedback-loop problems.

## Concurrency
- Normal TTY output relies on TTY locking.
- Console output can race with TTY output and uses `tm_mtx` spin locking when `TF_CONS` is set.
- Separate lock macros distinguish generic, TTY-side, and console-side paths.

## Filesystem Relevance
Not filesystem-specific, but it is part of the kernel’s common I/O surface and console diagnostics path used during filesystem/storage errors, boot logs, and debugger interaction.
