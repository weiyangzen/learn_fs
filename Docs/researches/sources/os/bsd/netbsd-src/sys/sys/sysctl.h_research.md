# File Research: sources/os/bsd/netbsd-src/sys/sys/sysctl.h

This large public/kernel header defines the NetBSD sysctl MIB interface, exported data structures, kernel sysctl tree APIs, and userland sysctl prototypes.

Key interface details:
- Defines hierarchy sizing: `CTL_MAXNAME`, `SYSCTL_NAMELEN`, dynamic allocation base, and initial child set size.
- Defines sysctl node types: node, int, string, quad, struct, bool, and ABI-dependent long.
- Defines access/behavior flags including read/write, private, permanent, own-data, immediate, hex, root, hidden, alias, mmap, description ownership, and unsigned.
- Defines meta-identifiers: query, create, destroy, mmap, describe.
- Defines top-level MIB nodes: `CTL_KERN`, `CTL_VM`, `CTL_VFS`, `CTL_NET`, `CTL_HW`, `CTL_USER`, `CTL_DDB`, `CTL_PROC`, `CTL_VENDOR`, `CTL_EMUL`, `CTL_SECURITY`.
- Defines extensive `KERN_*`, `HW_*`, `USER_*`, `DDBCTL_*`, `PROC_*`, and `EMUL_*` identifiers.

Important structures:
- `struct ctlname`
- `struct clockinfo`
- credential and process export structures: `ki_pcred`, `ki_ucred`, `eproc`, `kinfo_proc`, `kinfo_proc2`, `kinfo_lwp`
- kernel export structures: `kinfo_drivers`, `buf_sysctl`, `kinfo_file`, `evcnt_sysctl`, `hashstat_sysctl`
- VM map export structure: `kinfo_vmentry`
- kernel sysctl infrastructure: `ctldebug`, `sysctl_setup_chain`, `sysctlnode`, `sysctldesc`

Kernel APIs:
- Sysctl lifecycle: `sysctl_init`, `sysctl_basenode_init`, `sysctl_finalize`.
- Dispatch and locking: `sysctl_lock`, `sysctl_dispatch`, `sysctl_unlock`, `sysctl_relock`.
- Tree operations: locate, query, create, destroy, lookup, describe.
- Variadic create/destroy APIs: `sysctl_createv`, `sysctl_destroyv`.
- Copy helpers and standard handler stubs.

Userland APIs:
- `sysctl`
- `sysctlbyname`
- `sysctlgetmibinfo`
- `sysctlnametomib`
- `proc_compare`
- allocating helpers `asysctl` and `asysctlbyname`

Research notes:
- This file is a major ABI boundary. Many structures are explicitly padded or pointer-normalized for 32/64-bit compatibility.
- Filesystem relevance includes `CTL_VFS`, vnode/file/buffer exports, mount/statvfs-adjacent kernel data, and VM entry path reporting.
- Kernel module code commonly depends on the `SYSCTL_SETUP` and `sysctl_createv` patterns to publish tunables and statistics.
