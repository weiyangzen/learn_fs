# sources/test-tools/xfstests-bld/fstests-bld/android-compat/quotactl.c

Purpose: implements `quotactl` on Android by forwarding directly to the kernel syscall.

Important APIs and functions: exports `int quotactl(int cmd, const char *special, int id, caddr_t addr)` and defines `__NR_quotactl` for aarch64 if missing.

Control flow: includes syscall headers and returns `syscall(SYS_quotactl, cmd, special, id, addr)`.

State and persistence: no local state; modifies/query quota state through the kernel.

Dependencies and integration: depends on syscall numbers and `quota.h`; compiled into the Android compatibility library for quota-tools and xfstests.

Risks: uses `SYS_quotactl` while conditionally defining `__NR_quotactl`; portability depends on headers mapping the macro. Non-aarch64 targets without a definition hit a preprocessor error.

Test signals: quota tools link, and runtime quota operations return kernel syscall results.
