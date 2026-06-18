# File Research: sources/os/bsd/openbsd-src/sys/sys/malloc.h

Defines OpenBSD kernel malloc accounting classes, allocator flags, statistics ABI, and kernel allocation prototypes.

Key contents:
- Sysctl identifiers for `kern.malloc`.
- Allocation flags: `M_WAITOK`, `M_NOWAIT`, `M_CANFAIL`, `M_ZERO`.
- Memory type IDs and `INITKMEMNAMES`, including VFS/filesystem classes such as `M_MOUNT`, `M_VNODE`, `M_UFSMNT`, `M_NFSMNT`, `M_MSDOSFSMNT`, `M_FUSEFS`, `M_UDFMOUNT`, and NTFS classes.
- Statistics structures `kmemstats`, `kmemusage`, and `kmembuckets`.
- Kernel allocator constants and address-to-usage macros.

Key APIs:
- `malloc()`, `mallocarray()`, `free()`.
- `sysctl_malloc()`, `malloc_printit()`.
- Poisoning helpers: `poison_mem()`, `poison_check()`, `poison_value()`.

Risk notes:
- `M_LAST` and `INITKMEMNAMES` must stay aligned with memory type IDs.
- Kernel callers must pass the correct memory type and allocation flags for accounting and sleep behavior.
