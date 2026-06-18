# sources/security-integrity/selinux/libselinux/src/avc_internal.h

Purpose: This header defines AVC-internal callback plumbing, global state declarations, logging helpers, lock/memory/thread adapters, cache-stat macros, audit-buffer sizing, and internal cache-control prototypes.

Important APIs/types/functions: `set_callbacks()` installs optional user-supplied memory, log, audit, thread, and lock callbacks. Inline wrappers `avc_malloc()`, `avc_free()`, `avc_create_thread()`, `avc_alloc_lock()`, and lock operations fall back to libc/no-op behavior. `avc_log` and `avc_suppl_audit()` route messages through AVC-specific callbacks or libselinux defaults. Prototypes expose `avc_ss_grant`, revoke/reset, and audit mask updates.

Control flow: callers initialize function pointers once through `set_callbacks()`, then all AVC implementation code uses wrapper functions rather than direct malloc/free/log/lock calls. `AVC_CACHE_STATS` gates whether stat counters are incremented or compiled to no-ops.

State and persistence: declares external callback pointers, `avc_prefix`, `avc_running`, `avc_enforcing`, and `avc_setenforce`. The header itself has no persistent storage but centralizes access to process-global AVC state.

Dependencies and integration: includes public `selinux/avc.h`, `callbacks.h`, and libselinux logging. It is included by `avc.c`, `avc_internal.c`, and SID table code.

Risks and test signals: callback pointer combinations can produce partial customization, so tests should cover default operation and all supplied callback classes. Lock callbacks may be no-ops, making thread-safety application-dependent. Compile tests with and without `AVC_CACHE_STATS` are useful.
