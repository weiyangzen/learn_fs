# File Research: sources/os/bsd/dragonflybsd/sys/sys/sysctl.h

Public and kernel sysctl interface definitions.

Key responsibilities:
- Defines sysctl name hierarchy limits and type encodings:
  - `CTL_MAXNAME`
  - `CTLTYPE_*`
  - `CTLFLAG_*`
  - bitfield type helpers
- Defines top-level MIB identifiers:
  - `CTL_SYSCTL`, `CTL_KERN`, `CTL_VM`, `CTL_VFS`, `CTL_NET`, `CTL_HW`, `CTL_USER`, `CTL_LWKT`, etc.
- Defines many second-level constants under `KERN_*`, `KERN_PROC_*`, `KIPC_*`, `HW_*`, `USER_*`, and `CTL_P1003_1B_*`.
- In kernel builds, defines:
  - `struct sysctl_req`
  - `struct sysctl_oid`
  - sysctl handler prototypes
  - static OID construction macros
  - dynamic OID/context APIs
  - common sysctl root declarations
- In user/virtual-kernel-visible builds, declares:
  - `sysctl`
  - `sysctlbyname`
  - `sysctlnametomib`

Important invariants:
- `CTL_MAXNAME` caps integer MIB depth at 12.
- `OID_AUTO` enables dynamic numbering through linker-set registration.
- `SYSCTL_OID` instances are placed in `DATA_SET(sysctl_set, ...)`.
- Several scalar helpers automatically add `CTLFLAG_NOLOCK`.
- `NO_SYSCTL_DESCR` strips descriptions at compile time.
- Kernel sysctl lock macros use per-CPU `gd_sysctllock`.

Research notes:
- This header is both user ABI and kernel registration framework.
- The macro layer hides most static-tree construction details; dynamic OIDs are tracked with `sysctl_ctx_list`.
- The `FEATURE()` macro standardizes read-only feature booleans under `kern.features`.
