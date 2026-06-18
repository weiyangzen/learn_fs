# sources/test-tools/stress-ng/core-shim.h

Purpose: declares the compatibility types, constants, structs, and `shim_*` API used throughout stress-ng to isolate OS/libc/kernel variation.

Important APIs/types/functions: the header defines fallback kernel typedefs, shim rlimit/priority/itimer types, `shim_loff_t`/`shim_off64_t`, directory type constants, many `SHIM_MADV_*`, `SHIM_POSIX_MADV_*`, and `SHIM_POSIX_FADV_*` constants, fallback structs for `clone3`, getcpu cache, futex waitv, linux dirents, sched_attr, statx, ustat, timex, pollfd, xattr args, file attrs, namespace IDs, and the complete extern surface for shim wrappers.

Control flow: no runtime code except `shim_unconstify_ptr`, which safely casts away const through a union for legacy APIs. Compile-time guards select native types or local struct definitions.

State and persistence: no owned state. It defines types passed to syscalls that may mutate kernel/process state through implementation functions.

Dependencies/integration: includes uio, poll, dirent, sched, resource, and many stress-ng attribute macros. Nearly every low-level stressor can include this header to avoid direct platform-specific syscall declarations.

Risks: fallback struct definitions must track kernel ABI layouts closely enough for syscall use. New constants can collide if system headers later define different values. The enormous API surface makes stale declarations a risk when implementation signatures change.

Test signals: compile on old/new Linux headers, BSD/macOS-like platforms, static builds, and with feature macros toggled. ABI-sensitive tests should call statx, sched_attr, futex_waitv, xattrat, and namespace wrappers where available.
