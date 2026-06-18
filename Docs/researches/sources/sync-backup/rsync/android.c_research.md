# sources/sync-backup/rsync/android.c

Purpose: Android-specific runtime probe for whether `openat2()` is usable under Bionic/seccomp.

Important APIs/types/functions: public `openat2_usable()`; Android-only static `openat2_probe_handler()` and `sigjmp_buf`.

Control flow: on Android builds with `HAVE_OPENAT2`, the function installs a temporary `SIGSYS` handler, attempts `syscall(SYS_openat2, AT_FDCWD, ".", ...)`, records success/failure in a static cache, restores the old handler, and returns the cached result. On other platforms it returns 1.

State and persistence: static in-process cached result; no persistence.

Dependencies/integration: used by secure relative open code to avoid process death from trapped syscalls. Depends on `setjmp`, `sigaction`, Linux `openat2.h`, and Android compile-time macro.

Risks: temporary signal-handler changes are process-global; the probe is cached but not explicitly synchronized. It is intentionally Android-only because non-Android missing syscalls return errors instead of SIGSYS.

Test signals: Android static workflow compiles this path; runtime behavior is smoke-tested only through `rsync --version` under qemu.
