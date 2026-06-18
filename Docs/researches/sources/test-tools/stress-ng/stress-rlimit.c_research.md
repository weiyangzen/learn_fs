# sources/test-tools/stress-ng/stress-rlimit.c

Purpose: implements `rlimit`, an OS stressor that repeatedly sets resource limits and deliberately triggers limit-related faults/signals inside an OOM-manageable child.

Important APIs/types/functions: `stress_rlimit_info` is `CLASS_OS`, `VERIFY_ALWAYS`. `stress_limits_t` stores target and saved rlimit values for CPU, file size, address space, data, stack, and nofile when available. `stress_resource_id_t` enumerates resource IDs for get/set round trips. `stress_rlimit_handler()` long-jumps out of SIGSEGV/SIGXCPU/SIGXFSZ. `stress_rlimit_child()` performs the actual limit triggering.

Control flow: the parent installs signal handlers, creates an unlinked temp file, saves original limits, then runs `stress_rlimit_child()` through `stress_oomable_child()`. The child maps an alternate signal stack, synchronizes, repeatedly validates getrlimit/setrlimit for known resources, probes an invalid resource ID, sets tight limits, and randomly triggers file-size, address-space, data, stack, or fd exhaustion. Signals return through `sigsetjmp()` and increment bogo operations.

State and persistence: process state includes global jump control, signal handlers, an alternate stack, saved limits, and an unlinked temp file descriptor. Cleanup restores signal handlers, closes fds, removes the temp directory, and unmaps the signal stack.

Dependencies and integration points: requires `siglongjmp` support. It integrates with stress-ng mincore, mmap, OOM child handling, signal helpers, temp filesystem helpers, and shim rlimit abstractions.

Risks and test signals: signal/jump behavior is delicate, especially around stack and address-space exhaustion. Some platforms lack specific rlimits. Signals are expected SIGSEGV/SIGXCPU/SIGXFSZ recovery, bogo increments after trapped faults, no permanent parent limit corruption, and no temp file leakage.
