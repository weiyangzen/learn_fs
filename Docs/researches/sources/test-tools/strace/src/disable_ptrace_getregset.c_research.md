<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/disable_ptrace_getregset.c -->
## sources/test-tools/strace/src/disable_ptrace_getregset.c

Purpose: Specializes the ptrace-disabling helper to reject register-fetch requests used by strace, choosing `PTRACE_GETREGSET` on x86_64 when old getregs support exists.

Important APIs and types: Includes `defs.h`, temporarily redefines `static` to expose `getregs_old.h` configuration, conditionally defines `DISABLE_PTRACE_REQUEST PTRACE_GETREGSET`, then includes `disable_ptrace_request.c`.

Control flow: Compile-time logic chooses the request macro. Runtime flow is inherited from the seccomp template.

State and persistence: No local runtime state.

Dependencies and integration: Supports tests for register-fetch fallback paths, especially around old vs regset APIs.

Risks: The `#define static` include trick is delicate and can be affected by changes in `getregs_old.h`.

Test signals: Tests should confirm the built helper blocks the intended register request on supported architectures and reports unsupported otherwise.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/disable_ptrace_getregset.c -->
