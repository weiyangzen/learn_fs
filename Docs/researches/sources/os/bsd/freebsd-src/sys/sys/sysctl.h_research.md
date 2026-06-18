# File Research: sources/os/bsd/freebsd-src/sys/sys/sysctl.h

## Purpose
`sysctl.h` defines the FreeBSD sysctl MIB ABI and kernel registration framework for hierarchical tunables, statistics, and information nodes.

## Main Interfaces
- Defines sysctl type bits, access flags, security flags, tunable/statistics flags, capability-mode flags, and `OID_AUTO`.
- Kernel structures include `sysctl_req`, `sysctl_oid`, RB-tree `sysctl_oid_list`, and dynamic context tracking via `sysctl_ctx_list`.
- Declares generic handlers for bool, integer widths, long, string, opaque data, counters, UMA zone values, time conversions, and per-CPU values.
- Static and dynamic registration macros create root nodes, nodes, strings, const strings, bools, signed/unsigned integer widths, long/ulong, quad/uquad, counters, counter arrays, opaque data, structs, procedures, UMA zone controls, time conversions, feature flags, and `debug.sizeof` entries.
- Top-level numeric identifiers cover `CTL_SYSCTL`, `CTL_KERN`, `CTL_VM`, `CTL_VFS`, `CTL_NET`, `CTL_DEBUG`, `CTL_HW`, `CTL_MACHDEP`, `CTL_USER`, and `CTL_P1003_1B`.
- Userland declares `sysctl()`, `sysctlbyname()`, and `sysctlnametomib()`.

## Implementation Notes
Kernel OIDs are stored in linker sets for static registration and in RB trees for sibling lookup. Macros use compile-time assertions to check declared type, pointee size, and writeability constraints. `CTLFLAG_MPSAFE` versus `CTLFLAG_NEEDGIANT` enforcement is present but disabled behind `notyet`.

## Dependencies and Constraints
Kernel builds include queue/tree/linker-set and assert infrastructure; userland builds include `sys/cdefs.h` and `sys/_types.h`. Dynamic OIDs can be tracked in contexts for cleanup. The `CTL_VFS` top-level ID is the namespace root for filesystem sysctls.
