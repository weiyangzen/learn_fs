# sources/user-network-fs/samba/source3/lib/per_thread_cwd.c

## Purpose
This file provides a runtime gate for per-thread current working directories on platforms that support `unshare(CLONE_FS)`. Samba helper threads can isolate their CWD from the process main thread when the platform and container policy allow it.

## Important APIs, Types, And Functions
`per_thread_cwd_check()` must be called first, normally before threads are created. It attempts `unshare(CLONE_FS)` once when `HAVE_UNSHARE_CLONE_FS` is available, caches support in `_per_thread_cwd_supported`, and disables activation for the calling main thread. `per_thread_cwd_supported()` asserts the check was done and returns the cached result. `per_thread_cwd_disable()` marks the current thread as not allowed to activate. `per_thread_cwd_activate()` asserts prior checking/support and calls `unshare(CLONE_FS)` once per helper thread.

## Control Flow
Support discovery is cached globally in `_per_thread_cwd_checked`. Per-thread state uses `__thread` booleans for disabled and activated state. Activation is idempotent per thread but forbidden after disabling. Without compile-time support, activation panics.

## State And Persistence
State is only process memory. The externally visible effect is kernel task filesystem-context separation, affecting future `chdir` behavior for the calling thread. There is no disk persistence.

## Dependencies And Integration Points
The file depends on Samba assertions and optionally Linux `<sched.h>`. It is intended for startup and helper-thread code paths that need CWD changes without disturbing other threads.

## Risks And Test Signals
The runtime check can permanently unshare the main thread during probing, which is intentional but means call order matters. Container security policy can block `unshare` even when headers expose it. Tests should verify check-before-query assertions, unsupported platform panic behavior, idempotent activation, disable-before-activate assertion, and behavior after fork where `per_thread_cwd_disable()` marks the new main thread.
