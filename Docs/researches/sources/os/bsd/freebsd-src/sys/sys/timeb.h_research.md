# File Research: sources/os/bsd/freebsd-src/sys/sys/timeb.h

Deprecated System V/BSD `ftime(2)` compatibility header.

Key responsibilities:
- Emits a GCC warning for includes of this deprecated header outside libutil internals.
- Defines `time_t` if needed.
- Defines `struct timeb` with seconds, milliseconds, timezone minutes west of UTC, and DST flag fields.
- Declares userland `ftime(struct timeb *)` when not compiling kernel code.

Dependencies:
- Includes `sys/_types.h`; userland prototypes use `sys/cdefs.h`.

Notable risks:
- Retained solely for compatibility; new code should not depend on millisecond-era `ftime()` semantics.
- The warning is intentionally suppressed for `_IN_LIBUITL`, preserving build compatibility for internal legacy users.
