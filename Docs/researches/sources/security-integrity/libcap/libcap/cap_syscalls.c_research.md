## sources/security-integrity/libcap/libcap/cap_syscalls.c

Purpose: weak fallback for `psx_load_syscalls()` when libcap is not linked with libpsx.

Important APIs/functions: weak `psx_load_syscalls()` and internal `_libcap_overrode_syscalls`.

Control flow: when called with syscall function pointer slots, simply sets `_libcap_overrode_syscalls = 0`; if libpsx is linked, its strong symbol overrides this fallback and installs all-thread syscall wrappers instead.

State/persistence: mutates one process-global internal flag.

Dependencies/integration: `cap_proc.c` constructor path calls `cap_set_syscall(NULL,NULL)`, which calls this symbol.

Risks: correctness of POSIX thread semantics depends on link resolution; without libpsx, libcap falls back to libc/raw single-thread semantics.

Test signals: build with and without libpsx/pthreads, verify `_libcap_overrode_syscalls` behavior indirectly through psx tests and threaded UID/cap changes.
