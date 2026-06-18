# sources/security-integrity/libcap/psx/libpsx.h

Purpose: private header for the C PSX implementation.

Important APIs/types: defines `_psx_gettid()`, `_psx_sched_yield()`, atomic spinlock macros, `psx_tracker_state_t`, `psx_thread_ref_t`, and `psx_tracker_t`. Declares hidden coordination functions `psx_lock()`, `psx_unlock()`, `psx_cond_wait()`, `psx_mix()`, `psx_actions_size()`, and `psx_confirm_sigaction()`.

Control flow/state model: `psx_tracker_t` is the global state machine for a process, tracking PID, `/proc/<pid>/task` path, current state, signal number, active syscall command, handler action storage, thread hash map, and mismatch sensitivity.

Dependencies and integration: included by `psx.c` and `psx_calls.c`; it deliberately keeps signal action internals opaque because `psx_calls.c` uses raw kernel layouts.

Risks and test signals: custom spinlock/yield behavior and hash map collision expansion are concurrency-sensitive. The tests stressing thread churn, fork, and cgo errno expose regressions.
