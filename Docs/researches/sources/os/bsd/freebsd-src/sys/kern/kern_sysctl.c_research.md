# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_sysctl.c

Read status: complete file reviewed.

This file implements FreeBSD's kernel `sysctl(9)` MIB tree: OID registration, dynamic sysctl contexts, name/OID lookup, request dispatch, typed value handlers, kernel/user copy plumbing, tunable loading, VNET tunable refresh, and optional DDB inspection.

Core state is the root `sysctl__children` red-black tree plus per-OID child trees. `sysctllock` is a sleepable rmlock protecting the MIB and dynamic contexts, `sysctlmemlock` serializes large unprivileged user buffers, and `sysctlstringlock` protects writable string nodes. Dynamic OID memory comes from `M_SYSCTLOID`, request scratch from `M_SYSCTL`/`M_SYSCTLTMP`.

Registration paths include `sysctl_register_oid`, `sysctl_register_disabled_oid`, `sysctl_enable_oid`, `sysctl_unregister_oid`, `sysctl_add_oid`, `sysctl_remove_oid`, `sysctl_remove_name`, `sysctl_rename_oid`, `sysctl_move_oid`, and context helpers. Auto-numbered OIDs are assigned while preserving numeric order; duplicate named nodes increment refcounts, while leaf reuse is warned. Dynamic removal waits for running handlers via `oid_running` and `CTLFLAG_DYING`.

Tunable support builds dotted paths from OID parents and fetches loader/kernel environment values for numeric and string CTLTYPEs. VNET builds add `setenv`/`unsetenv` event handlers that refresh or restore per-vnet tunables when CTLFLAG_VNET tunables change.

The internal `CTL_SYSCTL` "staff" interface implements tree walking and metadata queries: debug dump, numeric-to-name, next/nextnoskip traversal, name-to-OID, format, description, and label. `name2oid` resolves dotted names under the lock and respects node handlers as terminal nodes.

`sysctl_root` is the central dispatcher. It resolves the OID, rejects writes to read-only nodes, enforces Capsicum `CTLFLAG_CAPRD/CAPWR`, securelevel, jail/VNET/write privileges, optional MAC checks, VNET arg rebasing, and handler Giant requirements before dropping the tree lock around the handler. Dynamic handler execution increments `oid_running` so unload/removal can wait safely.

The generic handlers cover bool, 8/16/32/int/long/64-bit integers, strings, opaque structs, and unit-conversion helpers for milliseconds-to-ticks, micro/milliseconds-to-sbintime, and seconds-to-timeval. String handling snapshots writable strings under `sysctlstringlock`; opaque handling retries copies if the thread generation changes during output.

Request plumbing includes `kernel_sysctl`, `kernel_sysctlbyname`, `userland_sysctl`, `sys___sysctl`, and `sys___sysctlbyname`. User requests use copyin/copyout functions, optional page wiring via `sysctl_wire_old_buffer`, KTRACE logging, CURVNET scoping, and EAGAIN retry/yield loops. Kernel requests use direct bcopy transfer functions.

With DDB enabled, the file adds a `show sysctl` debugger command that resolves named OIDs, walks subtrees, invokes safe handlers with debugger-specific output functions, supports name/value/opaque/hex modifiers, and skips unsafe handlers while recursing.

Risk areas are lock transitions around handler invocation, dynamic OID removal while modules unload, exact `oldidx/newidx` accounting across kernel/user copy paths, string updates under concurrent readers, VNET tunable restore ordering, and metadata leakage through capability-mode tree-walk interfaces.
