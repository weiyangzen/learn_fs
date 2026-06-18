<!-- BEGIN_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/setexecfilecon.c -->
# sources/security-integrity/selinux/libselinux/src/setexecfilecon.c

## Purpose
Computes and sets the process exec context for executing a file, with an RPM script fallback type helper.

## Important APIs, Types, And Functions
`setexecfilecon()` gets the current process context, file context, computes a process transition with `security_compute_create()`, falls back by replacing the current context type with `fallback_type` if no transition occurs, and calls `setexeccon()`. `rpm_execcon()` sets `rpm_script_t` and then `execve()`s.

## Control Flow
If SELinux is disabled it returns success. Errors during computation or setting are tolerated in permissive mode by returning success.

## State And Persistence Behavior
Sets the kernel per-thread exec context through procattr so the next exec uses it. No disk state is changed.

## Dependencies And Integration Points
Uses process/file context getters, context manipulation, class string lookup for `process`, transition computation, procattr setters, and optional RPM integration.

## Risks And Test Signals
Risks include fallback type producing invalid contexts, permissive-mode masking errors, and file context retrieval on symlinks or missing files. Tests should cover disabled/permissive/enforcing modes, default transition and fallback paths, invalid fallback types, and execcon clearing after use by callers.
<!-- END_FILE_RESEARCH: sources/security-integrity/selinux/libselinux/src/setexecfilecon.c -->
