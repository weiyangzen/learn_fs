<!-- BEGIN_FILE_RESEARCH: sources/test-tools/stress-ng/stress-bad-altstack.c -->
# sources/test-tools/stress-ng/stress-bad-altstack.c

Purpose: `stress-bad-altstack.c` implements the `bad-altstack` stressor. It deliberately installs invalid alternate signal stacks and provokes faults so the kernel's signal-stack handling kills or rejects child processes cleanly.

Important APIs/types/functions: the implementation requires `sigaltstack()`. Optional `getauxval(AT_SYSINFO_EHDR)` is used to test a VDSO-backed bad stack. Global stack mappings are `stack`, `zero_stack`, and optional `bus_stack`. `stress_bad_altstack_force_fault()` reads/writes through a chosen stack address. `stress_bad_altstack_signal_handler()` runs on the signal path, unmaps stacks, fills a large local array, and `siglongjmp`s back if the handler survived. `stress_bad_altstack_child()` tries invalid flags, too-small stacks, protected stacks, NULL/text/VDSO stacks, `/dev/zero` mappings, file mappings that can bus-error, and unmapped stacks.

Control flow: the parent maps the main alt stack, optional tmpfile-backed bus-error stack, and `/dev/zero` read-only stack, forces lazy `munmap` resolution, waits at the sync barrier, and repeatedly forks children. Each child installs signal handlers and performs several randomized bad-stack attempts. The parent waits; a child death by `SIGSEGV` is considered expected and increments bogo operations, `SIGKILL` can be handled as OOM depending on flags, and non-success exits fail the stressor.

State and persistence behavior: stack mappings are process address-space state only. Optional tmpfile mappings use `O_TMPFILE`; no named file is persisted. The child unmaps inherited global mappings in the signal handler; the parent cleans up remaining mappings at finish.

Dependencies and integration points: it uses stress-ng mmap, madvise, out-of-memory adjustment, signal wrappers, parent-death alarms, scheduler settings, temp paths, and process-state tracking. It registers `CLASS_VM | CLASS_MEMORY | CLASS_OS` with `VERIFY_ALWAYS` and an unimplemented fallback without `sigaltstack()`.

Risks: this code intentionally invokes undefined and architecture-specific fault behavior. Some BSD kernels can raise `SIGILL`; OpenBSD may reject stack setup and is treated as success. Unmapping globals from a signal handler is fragile but intentional. OOM-killer handling can hide true failures if the process is killed with `SIGKILL`.

Test signals: expected progress is repeated child `SIGSEGV` termination. Good coverage includes builds with and without `O_TMPFILE`, `MAP_STACK`, `mprotect`, VDSO auxv support, and `SIGXCPU`/`RLIMIT_CPU`, plus immediate-stop handling during fork loops.
<!-- END_FILE_RESEARCH: sources/test-tools/stress-ng/stress-bad-altstack.c -->
