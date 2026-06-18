# File Research: sources/os/bsd/dragonflybsd/sys/kern/tty_conf.c

## Summary
Defines the tty line-discipline switch table and registration hooks for loadable disciplines.

## Main Responsibilities
- Provides `linesw[MAXLDISC]`, with discipline 0 wired to the standard termios tty discipline from `tty.c`.
- Fills unused/defunct slots with `NODISC` stubs returning `ENODEV` or `ENOIOCTL`.
- Exposes `ldisc_register` and `ldisc_deregister` under `tty_token`.
- Provides `l_nullioctl`, `l_noread`, and `l_nowrite` fallback helpers.

## Important Behavior
`ldisc_register(LDISC_LOAD, ...)` scans loadable slots starting at index 7 and installs a supplied `struct linesw`. Deregistration resets the slot to `nodisc`.

## Risks
The table is global and fixed-size. The `LDISC_LOAD` scan keeps assigning `slot` through the loop, so it chooses the last matching free loadable slot rather than the first. Active tty users of a discipline are not tracked here; callers must coordinate unload safety elsewhere.
