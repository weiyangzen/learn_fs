# sources/test-tools/xfstests-bld/fstests-bld/android-compat/ustat.c

Purpose: provides an Android wrapper for the legacy `ustat` syscall.

Important APIs and functions: exports `int ustat(dev_t dev, struct ustat *ubuf)`.

Control flow: returns `syscall(SYS_ustat, dev, ubuf)`.

State and persistence: queries kernel filesystem statistics for a device; no local state.

Dependencies and integration: includes `ustat.h` and syscall headers; installed with android-compat for tools still referencing `ustat`.

Risks: `ustat` is obsolete and may be unavailable on some architectures/kernels. Callers should handle `ENOSYS`.

Test signals: link success and runtime syscall return matching target kernel support.
