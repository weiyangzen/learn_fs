# sources/security-integrity/encfs/src/security.rs

Purpose: provides process-level hardening helpers intended to reduce key-material exposure through core dumps, ptrace/proc memory reads, debugger attachment, and swap.

Important APIs/types/functions: `harden_process()` is the public startup hook and calls `disable_core_dumps()` plus `set_nondumpable()`. `lock_memory()` is a separate public hook that calls `mlockall(MCL_CURRENT | MCL_FUTURE)`. Platform-specific `set_nondumpable()` branches use Linux `prctl(PR_SET_DUMPABLE, 0)`, FreeBSD `procctl(PROC_TRACE_CTL_DISABLE)`, and macOS `ptrace(PT_DENY_ATTACH)`.

Control flow: each helper calls a libc primitive inside `unsafe`, checks for nonzero return codes, and logs warnings rather than returning errors or aborting. `harden_process()` intentionally does not call `lock_memory()`, leaving memory locking opt-in because it may require elevated limits or capabilities.

State and persistence: changes apply to the current process and, for `mlockall(MCL_FUTURE)`, future mappings. No repository or config state is persisted. Failure state is only logged.

Dependencies and integration points: depends on `libc` and `log::warn`. It should be called early in `main()` before sensitive keys are derived or loaded. It complements crypto code but does not wipe secrets itself.

Risks: warning-only failures can leave the process less hardened without preventing normal operation. `mlockall` can fail under default `RLIMIT_MEMLOCK`; tests or low-memory environments may observe warnings. The macOS `PT_DENY_ATTACH` behavior can disrupt debugging. No Windows equivalent is provided.

Test signals: this file has no direct tests in the subset. Its behavior is mostly platform integration and should be validated by startup smoke tests that assert no fatal regressions, plus manual or privileged checks for memory-lock/core-dump settings.
