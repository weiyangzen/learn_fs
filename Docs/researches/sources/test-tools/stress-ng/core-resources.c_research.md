# sources/test-tools/stress-ng/core-resources.c

Purpose: allocates, lightly exercises, and frees many kernel and libc resource types to pressure resource accounting, cleanup paths, and limit handling in stressors.

Important APIs/types/functions: `stress_resources_allocate` creates up to `num_resources` entries of `stress_resources_t`. `stress_resources_access` touches/queries allocated resources. `stress_resources_free` releases everything. `stress_resources_init` seeds sentinel values. A small pthread helper sleeps so a live thread resource exists in the first entry.

Control flow: allocation starts by initializing sentinels, enabling KSM merge, checking memory limits, and sizing mlock allowance from `RLIMIT_MEMLOCK`. Each iteration rechecks the global continue flag and minimum free memory, then conditionally/randomly allocates memory (`calloc`, `sbrk`, `mmap`, `memfd`, `memfd_secret`), descriptors (`pipe`, `/dev/null`, eventfd, sockets, socketpair, userfaultfd, tmpfile), inotify, PTY pairs, pthread/mutex/C11 mtx, timers, semaphores, SysV/POSIX queues, pkeys, pidfds, and optional child processes. After the loop it punches holes in anonymous mappings by unmapping all but one page. Free mirrors every sentinel and closes/unmaps/destroys/removes/kills in-place. Access writes to memory regions and performs harmless `fcntl(F_GETFL)`/`kill(pid,0)` probes where available.

State and persistence: state is per-entry in the caller-provided array. Some resources have kernel persistence until explicitly removed, such as SysV semaphores/message queues and POSIX mqueues; the free path removes them. Temporary child processes sleep and are killed/waited on cleanup.

Dependencies/integration: heavy use of shim wrappers, `core-madvise`, `core-mincore`, `core-killpid`, pthread and optional OS headers. It integrates with stressors that want broad resource pressure without duplicating setup/cleanup logic.

Risks: partial allocation is expected, so sentinel correctness is critical. A notable cleanup dependency is the nested pidfd getfd close under pidfd close guards; if pidfd open failed but getfd somehow held a descriptor, cleanup would miss it. Random allocation means coverage is nondeterministic unless the RNG is controlled. `sbrk` allocations are recorded but not explicitly restored, so this intentionally perturbs process heap state.

Test signals: run under low limits, missing feature macros, interrupted continue flag, and `do_fork` true. Leak checks should include fd counts, SysV IPC objects, POSIX mqueue names, child process cleanup, and mapped-region counts before/after.
