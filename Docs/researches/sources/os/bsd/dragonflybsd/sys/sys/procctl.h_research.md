# File Research: sources/os/bsd/dragonflybsd/sys/sys/procctl.h

Process-control ABI for reapers, parent-death signals, and Solaris-compatible id types.

Key responsibilities:
- Defines `idtype_t` enum synchronized with Solaris values for process, parent PID, process group, session, class, UID, GID, all, LWP, task, project, pool, jail/zone, contract, CPU, and processor set identifiers.
- Defines reaper status, kill, and union information structures.
- Defines procctl command constants for acquiring/releasing reaper status, parent death signal control/status, and descendant kill.
- Defines reaper status and kill flags.
- Defines kernel `struct sysreaper` with lock, parent topology, owning process, flags, and references.
- Declares userland `procctl()`.

Important behavior:
- `_PROCCTL_PRESENT` advertises the interface.
- Reaper kill can target direct children only via `REAPER_KILL_CHILDREN`.
- Kernel structure exists only for kernel/kernel-structures builds.

Dependencies:
- Includes `sys/cdefs.h`.
- Kernel includes `sys/lock.h`; userland includes `sys/types.h`.

Notable risks:
- `idtype_t` numerical compatibility with Solaris/FreeBSD-style consumers is intentional.
- Reaper topology and refs must be maintained across process exit/reparenting.
