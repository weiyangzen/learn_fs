# File Research: sources/os/bsd/dragonflybsd/sys/kern/kern_plimit.c

This file manages per-process resource limits (`struct plimit`). It implements initialization, fork/LWP sharing rules, copy-on-write mutation, get/set rlimit syscalls, CPU-limit testing, and adjusted limit lookup for fork/chroot depth.

Core model:
- `struct plimit` instances are reference-counted and can be shared across forked processes.
- `PLIMITF_EXCLUSIVE` marks structures that must remain stable for threaded processes.
- Threads cache the current process limit in `td->td_limit`; `readplimits()` refreshes that cache when `p->p_limit` changes.

Important functions:
- `plimit_init0()` initializes proc0 limits to infinity, then caps `RLIMIT_NOFILE`, `RLIMIT_NPROC`, RSS, and memlock from kernel globals and free memory.
- `plimit_fork()` tries to share the parent's limit, but copies if the old limit is exclusive and cannot safely be reused.
- `plimit_lwp_fork()` forces exclusivity when a new LWP is created so `p->p_limit` remains stable across process threads.
- `plimit_modify()` ensures exclusive ownership before optional in-place limit mutation.
- `plimit_free()` decrements the refcount and frees on last reference.
- `kern_setrlimit()` validates `which`, normalizes negative values to infinity, checks privilege when raising hard/current limits, clamps selected limits to kernel maxima, updates CPU microsecond limit, and adjusts stack VM protections when `RLIMIT_STACK` changes.
- `kern_getrlimit()` returns a copied limit, skipping checks for kernel-thread callers without `curproc`.
- `plimit_testcpulimit()` reports OK, soft `SIGXCPU` style action, or kill based on accumulated CPU time and limit values.
- `plimit_getadjvalue()` downscales `RLIMIT_NPROC` by process fork/chroot depth, up to 50 percent.

Concurrency:
- Process `p_spin` protects replacement in `readplimits()`.
- `p_limit->p_spin` protects limit field mutation for multi-threaded processes.
- Refcount transitions use atomics and CPU fences.

Filesystem/storage relevance:
- `RLIMIT_NOFILE`, `RLIMIT_FSIZE`, `RLIMIT_POSIXLOCKS`, memory limits, and process count limits affect filesystem-facing workloads, file descriptor pressure, and locking behavior.
