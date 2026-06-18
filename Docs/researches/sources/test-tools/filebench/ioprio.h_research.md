<!-- BEGIN_FILE_RESEARCH: sources/test-tools/filebench/ioprio.h -->
# sources/test-tools/filebench/ioprio.h

Purpose: exposes `set_thread_ioprio()` with a compile-time portability shim.

Important APIs: when `HAVE_IOPRIO` is set, declares the real function and includes Linux syscall definitions. Otherwise defines a static inline no-op accepting `threadflow_t *`.

Control flow: `flowop.c` can call `set_thread_ioprio()` unconditionally because this header erases the feature on unsupported builds.

State/persistence: no-op path has no state; enabled path delegates to `ioprio.c`.

Dependencies/integration: requires `threadflow_t` from prior `filebench.h` inclusion and build-system detection of `HAVE_IOPRIO`.

Risks: the header itself does not include `filebench.h`, so include order matters unless the including C file already has `threadflow_t`. Platform-specific `<asm/unistd.h>` may not expose expected syscall numbers on all Linux variants.

Test signals: compile matrix with `HAVE_IOPRIO` on/off and inclusion from files that have already included `filebench.h`.
<!-- END_FILE_RESEARCH: sources/test-tools/filebench/ioprio.h -->
