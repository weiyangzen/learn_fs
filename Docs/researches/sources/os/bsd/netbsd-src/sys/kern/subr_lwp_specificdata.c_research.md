# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_lwp_specificdata.c

Read completely: 139 lines.

Wraps the generic `specificdata(9)` facility to provide LWP-specific kernel data. A single domain is created by `lwpinit_specificdata()`, and subsystem keys can be created/deleted with optional destructors.

Core behavior:
- `lwp_initspecific()` initializes a new LWP's specific-data reference.
- `lwp_finispecific()` finalizes it and runs destructors as appropriate through the generic facility.
- `lwp_getspecific()` and `lwp_setspecific()` access the current LWP's data.
- `_lwp_getspecific_by_lwp()` and `lwp_setspecific_by_lwp()` access a supplied LWP.

Risks and notes:
- The file explicitly states LWP-specific data is not interlocked.
- An LWP should normally access only its own data; callers accessing another LWP must guarantee no concurrent get/set inconsistency.
