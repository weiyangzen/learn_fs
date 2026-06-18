# sources/security-integrity/libcap/psx/wrap/psx_wrap.c

Purpose: weak wrapper support for legacy `-Wl,--wrap=pthread_create` linkage.

Important APIs/functions: declares `__real_pthread_create()` and `__wrap_pthread_create()`. Defines weak `__real_pthread_create()` that checks whether it incorrectly resolves to the wrapper and otherwise calls `pthread_create()`.

Control flow: if wrapper linkage is wrong and `pthread_create` equals `__wrap_pthread_create`, it prints an error and exits 1. Otherwise it delegates to `pthread_create`.

State and dependencies: no persistent state. Depends on pthreads and linker wrap behavior.

Risks and test signals: mainly protects against mislinked legacy libpsx builds. Modern libpsx no longer requires pthread wrapping, but compatibility builds can catch configuration errors here.
