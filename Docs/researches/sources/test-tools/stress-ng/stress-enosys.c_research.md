# sources/test-tools/stress-ng/stress-enosys.c

Purpose: implements the `enosys` stressor, which searches syscall-number space for unimplemented system calls and verifies they return `ENOSYS` while avoiding known live or dangerous syscalls. On x86-64 Linux it can also exercise the raw `syscall` instruction path in addition to libc `syscall()`.

Important APIs/types/functions: `stress_hash_syscall_t` stores syscall numbers already known to be real or unsafe; `stress_enosys_rpc_t` is the pipe RPC payload exchanged between parent and child. `syscall_ignore[]` hard-skips clone/fork/reboot/vhangup-like calls, while the very large `skip_syscalls[]` table is a compile-time catalogue of known syscall numbers to avoid. `stress_enosys_syscall()` performs the actual call with seven `-1` arguments, optional `x86_64_syscall6()`, signal recovery, and child-escape detection. `stress_enosys_parent()`, `stress_enosys_child()`, and `stress_enosys_push_syscall()` implement the harness.

Control flow: `stress_enosys()` installs SIGPIPE handling, seeds the hash table with known syscall numbers, creates two pipes, forks a constrained child, and loops until the global stop condition. The parent chooses sequential, high, random, masked, and bit-pattern syscall numbers, writes each request, reads back errno/count, caches any non-`ENOSYS` result, increments bogo operations, and later kills the child. The child drops capabilities, makes shared mappings read-only, sets CPU/process limits and signal handlers, arms a short interval timer around each syscall, then returns the observed errno.

State and persistence behavior: no durable state is stored. Runtime state is a process-local hash table of skipped numbers, pipe messages, static syscall sequence counters, signal jump state, and aggregate syscall metrics. The child is disposable by design because unexpected syscalls may fork, fault, block, or mutate per-process state.

Dependencies and integration points: requires `sys/syscall.h` and `syscall()` support. It integrates with stress-ng capability dropping, OOM/fork retry, signal, CPU feature, read-only shared memory, scheduler, timing, metrics, and process-state helpers. The exported `stress_enosys_info` registers `CLASS_OS`.

Risks: calling arbitrary syscall numbers is inherently hazardous. The file mitigates this with skip tables, child isolation, capability dropping, resource limits, timers, signal longjmp, and explicit exit when a syscall unexpectedly creates a child, but new architectures or kernel syscall additions can make the skip tables stale. The x86 raw syscall path is architecture-sensitive and disabled outside guarded builds.

Test signals: build with and without syscall support, run short `--enosys` timeouts as non-root and root, verify nonzero `syscalls per second`, no leaked child processes, no unexpected real syscall side effects, and stable behavior on x86-64 with and without `syscall` CPU support.
