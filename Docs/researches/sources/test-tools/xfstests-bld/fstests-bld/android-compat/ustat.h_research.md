# sources/test-tools/xfstests-bld/fstests-bld/android-compat/ustat.h

Purpose: declares the legacy `ustat` interface and structure for Android builds.

Important APIs and functions: guarded header defining `struct ustat` with `f_tfree`, `f_tinode`, `f_fname`, and `f_fpack`, plus `ustat(dev_t, struct ustat *)` prototype.

Control flow: no runtime flow; preprocessor declarations only.

State and persistence: no state. Defines ABI shape for callers and `ustat.c`.

Dependencies and integration: installed as `sys/ustat.h` by the android-compat Makefile.

Risks: structure definition must match users' expectations; the legacy API is not suitable for new code and may not be implemented by target kernels.

Test signals: source files including `<sys/ustat.h>` compile under Android cross builds.
