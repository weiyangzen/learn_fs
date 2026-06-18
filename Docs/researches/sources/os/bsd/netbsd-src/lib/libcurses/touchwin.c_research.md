# File Research: sources/os/bsd/netbsd-src/lib/libcurses/touchwin.c

This libcurses file implements dirty-line tracking and synchronization helpers for `WINDOW` objects. It is responsible for marking windows or line ranges as changed, clearing dirty state, propagating touch state between parent/subwindows, and honoring `immedok`/`syncok` behavior.

Key entry points:
- `__sync(WINDOW *)` refreshes immediately when `__IMMEDOK` is set and propagates changes upward when `__SYNCOK` is set.
- `is_linetouched()` and `is_wintouched()` inspect `__ISDIRTY` line flags.
- `touchline()`, `wredrawln()`, `touchwin()`, `redrawwin()`, `untouchwin()`, and `wtouchln()` expose public touch/untouch operations.
- `__touchwin()` and `__touchline()` are internal helpers used by refresh/sync paths.
- `wsyncup()` marks ancestors dirty; `wsyncdown()` marks a child dirty if an ancestor is already touched.

Important state and control flow:
- The real work is in `_cursesi_touchline_force()`, which offsets columns by `win->ch_off`, sets `__ISDIRTY`, optionally sets `__ISFORCED`, and widens the shared `firstchp`/`lastchp` damage bounds.
- `wtouchln(..., changed = 0)` clears damage by resetting shared first/last changed-column pointers back to empty values and clearing `__ISDIRTY | __ISFORCED`.
- Parent and subwindow interaction matters because line damage pointers are shared; touching through one view affects refresh decisions for related windows.

Risks and notes:
- Several public wrappers call through to `wtouchln()` using `win->maxy` without an explicit NULL check in the wrapper itself; NULL safety depends on the callee, except `touchwin()`/`redrawwin()` dereference `win` before `wtouchln()`.
- `is_wintouched()` loops `y < maxy`, while `is_linetouched()` allows `line == maxy` to pass the `line > win->maxy` check; bounds conventions are worth checking against the rest of curses.
- This is display invalidation code, not filesystem code, but it is part of the NetBSD source tree covered by subset A.
