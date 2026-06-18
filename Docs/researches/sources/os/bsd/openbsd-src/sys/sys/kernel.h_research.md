# File Research: sources/os/bsd/openbsd-src/sys/sys/kernel.h

This header declares core kernel global variables.

Key definitions/declarations:
- Host identity globals: `hostid`, `hostname`, `hostnamelen`, `domainname`, `domainnamelen`.
- Time globals: `utc_offset`, `tick`, `tick_nsec`, `ticks`, `hz`, `stathz`, `profhz`.
- Default `HZ` value of 100 if not otherwise defined.

Behavior and integration:
- Intended for kernel global state consumers.
- Relies on `MAXHOSTNAMELEN` being available from prior includes.

Risk notes:
- These globals are widely shared kernel state; changes affect timekeeping, profiling, and host identity reporting.
