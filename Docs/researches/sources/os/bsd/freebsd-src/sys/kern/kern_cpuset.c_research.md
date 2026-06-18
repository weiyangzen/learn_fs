# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_cpuset.c

## Purpose
Implements FreeBSD CPU affinity and NUMA domain policy infrastructure: cpuset trees, per-thread anonymous masks, named set IDs, jail roots, kernel/default sets, interrupt affinity delegation, domainset interning, and cpuset/domain syscalls.

## Main Elements
- Cpuset model:
  - Comments define ROOT, CPUSET/base, and MASK levels.
  - `cpuset_getbase()` and `cpuset_getroot()` resolve anonymous and root sets.
  - `cpuset_ref()`, `cpuset_rel()`, deferred release helpers, and UMA zones manage cpuset lifetime.
  - `cpuset_lookup()` finds named sets and enforces jail visibility.
- Set creation and modification:
  - `cpuset_init()` initializes a set under a parent, intersects masks, validates domain policy, and inserts named sets into `cpuset_ids`.
  - `cpuset_create()` allocates a named set ID.
  - `cpuset_modify()` validates privilege, jail restrictions, root subset constraints, read-only flags, and recursively applies CPU-mask restrictions to children.
  - `cpuset_shadow()` creates anonymous per-thread sets to preserve private masks.
- Domainsets:
  - Static policies include first-touch, interleave, round-robin, fixed-domain, and prefer-domain sets.
  - `_domainset_create()` interns equivalent domainsets and precomputes iteration order.
  - `domainset_create()`, `domainset_valid()`, `domainset_restrict()`, `domainset_empty_vm()`, and `domainset_shadow()` validate, sanitize, and restrict NUMA policies.
  - `cpuset_modify_domain()` recursively propagates domain-policy changes and calls `domainset_notify()` to update thread policies.
- Process/thread updates:
  - `cpuset_which()` resolves PID, TID, TID-or-PID, cpuset ID, jail ID, IRQ, and domain targets with permission checks.
  - `cpuset_setproc()` performs two-pass process-wide changes, preallocating cpusets/domainsets before taking locks, then replacing each thread’s cpuset with deferred release.
  - `_cpuset_setthread()`, `cpuset_setthread()`, and `cpuset_setithread()` apply masks or domains to a single thread/interrupt thread.
- Initialization:
  - `domainset_init()` builds global NUMA policies.
  - `domainset_zero()` initializes the cpuset spin mutex and removes empty VM domains.
  - `cpuset_thread0()` creates system root set 0, default set 1, kernel set 2, and initializes `cpuset_root`.
  - `cpuset_kernthread()` moves kernel threads to the kernel set.
  - `cpuset_create_root()` and `cpuset_setproc_update_set()` support jail cpuset roots and rebasing processes into them.
- Syscalls and user APIs:
  - `sys_cpuset()` creates a new set for the current process.
  - `kern_cpuset_setid()` assigns a process to a named set.
  - `kern_cpuset_getid()` returns root/base/current set IDs.
  - `kern_cpuset_getaffinity()` and `kern_cpuset_setaffinity()` handle CPU masks for threads, processes, sets, jails, IRQs, interrupt handlers, and domains.
  - `user_cpuset_getaffinity()` and `user_cpuset_setaffinity()` handle variable-size user masks and high-bit validation/zeroing.
  - `kern_cpuset_getdomain()` and `kern_cpuset_setdomain()` expose NUMA domain masks and policies.
  - `domainset_populate()` validates user-provided domain masks and translates prefer policy into preferred-domain plus fallback semantics.
- Capability and tracing:
  - `cpuset_check_capabilities()` restricts capability-mode operations to current thread/process `CPU_LEVEL_WHICH` access and records ktrace failures.
  - PowerPC-specific wrappers avoid function-pointer issues with `copyin`/`copyout`.
- Debugging:
  - Optional DDB commands dump cpuset IDs, refs, flags, CPU masks, and domain policies.

## Dependencies And Integration
Integrates with scheduler affinity (`sched_affinity()`), process/thread locking, jails/prisons, Capsicum, ktrace, interrupt affinity (`intr_getaffinity()`/`intr_setaffinity()`), UMA, unr ID allocation, VM domain state, kernel object domain policy, allproc traversal, and syscall copy callbacks.

## Risk Notes
This is a central policy and locking file. It must avoid allocation under spin locks, preserve process-wide consistency across many threads, handle anonymous set sharing safely, and never allow masks/domains outside parent/root/jail restrictions. Empty CPU masks return `EDEADLK`; invalid or out-of-scope masks return `EINVAL`/`ERANGE`. User mask size handling deliberately rejects nonzero high bits on set and zero-fills high bytes on get.
