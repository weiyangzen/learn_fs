# File Research: sources/os/bsd/netbsd-src/sys/sys/intr.h

Defines common interrupt constants and the kernel soft interrupt API. It exports `INTRIDBUF`, `INTRDEVNAMEBUF`, soft interrupt establishment/scheduling/disestablishment routines, MI/MD softint hooks, softint level flags, and legacy IPL/spl aliases.

The header bridges machine-independent soft interrupt code with `machine/intr.h`. User-visible exposure is minimal except `_KMEMUSER` access to `SOFTINT_COUNT`. Risks are mostly contract-related: MD ports must implement compatible softint trigger/dispatch behavior, and historical IPL aliases intentionally collapse old priorities onto modern NetBSD IPL levels.
