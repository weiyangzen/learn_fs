# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_evcnt.c

## Summary
Implements kernel event counter registration, detachment, sysctl export, and legacy interrupt counter bridging.

## Main Responsibilities
- Maintains the global `allevents` tail queue protected by `evcnt_lock`.
- Attaches static counters from the `evcnts` link set during `evcnt_init()`.
- Attaches dynamic counters with or without zeroing.
- Detaches counters and increments a generation number.
- Exports counters through `kern.evcnt` sysctl with type and nonzero filters.
- Optionally mirrors legacy `intrcnt`/`intrnames` arrays into dynamic event counters.

## Important Behavior
Sysctl export builds variable-length `evcnt_sysctl` records containing fixed fields plus group/name strings, rounded to 64-bit units. It copies out without holding `evcnt_lock`; if the generation changes during copyout, it retries up to 100 times before returning `EAGAIN`.

Kernel addresses in sysctl output are conditionally exposed through `get_expose_address(curproc)`.

## Dependencies
Uses link sets, `TAILQ`, `kmem`, sysctl, `copyout`, event counter ABI structures, and optional legacy interrupt counter symbols.

## Risks
Counters are exported as statistics only; concurrent attach/detach can force retries and eventually `EAGAIN`. Dynamic event callers must ensure the pointed-to group and name strings remain valid while attached.
