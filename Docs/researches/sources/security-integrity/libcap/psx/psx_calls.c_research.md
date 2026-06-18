# sources/security-integrity/libcap/psx/psx_calls.c

Purpose: low-level signal-handler installation and actor code for libpsx, isolated because it needs raw kernel sigaction layouts.

Important APIs/functions: defines architecture-specific `struct sigaction` compatibility, `psx_actions_t`, `psx_actions_size()`, `psx_posix_syscall_actor()`, and `psx_confirm_sigaction()`. Provides raw `rt_sigprocmask` and `rt_sigaction` wrappers and optional `SA_RESTORER` assembly trampolines.

Control flow: `psx_confirm_sigaction()` blocks the PSX signal, reads existing handler, chains it, installs `psx_posix_syscall_actor()` first, then restores the signal mask. The actor ignores unrelated signals by forwarding to the chained handler. For real PSX signals, it performs the active syscall, records retval/pending in the thread map, waits for command deactivation, decrements incomplete, and returns.

State and dependencies: uses global `psx_tracker`, raw `syscall()`, hidden signal 33, kernel signal ABI knowledge, and per-thread TIDs.

Risks and test signals: architecture ABI mismatch, handler chaining, signal races, and async-signal-safety are key risks. Thread churn and cgo tests stress the handler installation and fan-out.
