# File Research: sources/os/bsd/netbsd-src/sys/kern/tty_conf.c

## Purpose

`tty_conf.c` manages NetBSD line discipline registration, lookup, reference counting, and the built-in termios/ntty disciplines.

## Main Responsibilities

- Defines the default `termios` line discipline and the legacy-compatible `ntty` discipline.
- Initializes the line discipline list with the built-ins.
- Looks up disciplines by name or legacy number.
- Attaches and detaches dynamic line disciplines.
- Assigns legacy numeric discipline IDs.
- Provides default pass-through ioctl and error poll helpers.

## Core Data Model

`ttyldisc_list` is a global list of `struct linesw` entries protected by `tty_lock`. Built-in `termios_disc` and `ntty_disc` are considered static and are not refcounted. Dynamic disciplines use `l_refcnt` and cannot be detached while in use.

## Behavior

`ttyldisc_lookup()` and `ttyldisc_lookup_bynum()` return a held reference. `ttyldisc_release()` drops it. `ttyldisc_attach()` validates required callbacks, enforces name length and uniqueness, assigns a legacy number, and inserts the discipline. `ttyldisc_detach()` refuses removal while the discipline is static or referenced.

`ttyldisc_default()` returns the built-in termios discipline used by new ttys.
