# File Research: sources/os/bsd/dragonflybsd/sys/sys/cpumask.h

CPU mask public wrapper and CPU lock type definitions.

Key responsibilities:
- Imports machine `__cpumask_t` and exposes it as `cpumask_t`.
- For userland, maps `CPU_ZERO`, `CPU_SET`, `CPU_CLR`, `CPU_ISSET`, `CPU_COUNT`, `CPU_AND`, `CPU_OR`, `CPU_XOR`, and `CPU_EQUAL` to machine helpers.
- Defines `CPU_SETSIZE` from cpumask width.
- Defines public `cpulock_t` and bit/counter masks for a combined exclusive bit plus auxiliary count lock.

Dependencies:
- Includes `machine/cpumask.h` and `machine/stdint.h`.

Notable risks:
- `cpumask_t` width is machine-dependent, so public CPU set size follows architecture limits.
- `cpulock_t` is public because it appears near process structures; callers must honor bit layout.
