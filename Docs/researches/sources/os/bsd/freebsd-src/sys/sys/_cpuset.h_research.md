# File Research: sources/os/bsd/freebsd-src/sys/sys/_cpuset.h

CPU set type declaration.

Defines:
- In kernel builds, `CPU_SETSIZE` as `MAXCPU`.
- `CPU_MAXSIZE` as 1024 and default `CPU_SETSIZE` to that outside kernel-specific definition.
- `cpuset_t` as a bitset-backed `_cpuset`.

Research relevance:
- Small ABI/type bridge between generic bitset machinery and CPU affinity/set APIs.
