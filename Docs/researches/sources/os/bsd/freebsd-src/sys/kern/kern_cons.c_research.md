# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_cons.c

## Purpose
Provides machine-independent console management: probing and selecting low-level consoles, multiplexing console input/output, controlling console availability, exposing console selection through sysctl, redirecting console output to a tty, and providing optional system beep and vty selection support.

## Main Elements
- Console registration and selection:
  - `cninit()` initializes keyboard support, probes `cons_set`, chooses the best-priority console, supports `RB_MULTIPLE`, and enables boot-time pause mode.
  - `cnadd()`, `cnremove()`, and `cnselect()` manage the active console list and preferred console.
  - `cnavailable()` and `cnunavailable()` track input availability via `cons_avail_mask`.
- Runtime control:
  - `kern.console` sysctl lists active/available consoles and accepts console add/remove/select requests.
  - `kern.consmute` and boot flags control muted console output.
- Low-level I/O:
  - `cngetc()` blocks for console input.
  - `cncheckc()` polls all eligible consoles.
  - `cngets()` reads an editable line with normal, hidden, or password-style echo.
  - `cnputc()`, `cnputsn()`, and `cnputs()` write to all active consoles, add carriage returns before newlines, and serialize string output with `cnputs_mtx`.
  - `cngrab()`, `cnungrab()`, and `cnresume()` forward debugger/suspend lifecycle operations to console drivers.
- TTY redirection:
  - `constty_set()` attaches a tty as console output target and initializes `consmsgbuf`.
  - `constty_clear()` detaches the tty and flushes pending data back to the physical console.
  - `constty_timeout()` periodically drains `consmsgbuf` into the tty.
- Miscellaneous:
  - `sysbeep()` drives the timer speaker when available, otherwise returns `ENODEV`.
  - `vty_enabled()` chooses between `sc` and `vt` based on tunable/build availability.

## Dependencies And Integration
Uses console-driver `consdev` operations, linker set `cons_set`, keyboard initialization, DDB/KDB state, tty locking, callouts, msgbuf, sysctl, boot flags, timer speaker MD hooks, and optional `EARLY_PRINTF`.

## Risk Notes
Console paths run during early boot, panic/debugger contexts, and normal runtime, so locking is deliberately limited. `cnputsn()` drops recursive console prints to avoid deadlock. TTY redirection never frees `consbuf` because pending users may still reference it. Sysctl console switching has `CTLFLAG_NEEDGIANT`, reflecting legacy synchronization constraints.
