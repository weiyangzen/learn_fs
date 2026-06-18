# sources/test-tools/xfstests-bld/fstests-bld/android-compat/lio_listio.c

Purpose: provides a stub `lio_listio` symbol for builds that require librt linkage on Android.

Important APIs and functions: exports `int lio_listio(int mode, void *aiocb_list[], int nitems, void *sevp)`.

Control flow: prints a diagnostic to stderr and calls `abort()` unconditionally.

State and persistence: no persistent state; process terminates if the function is called.

Dependencies and integration: built into `librt.a`/shared librt by the android-compat Makefile to satisfy link-time references.

Risks: this is not a functional implementation. Any runtime path that calls `lio_listio` will abort the program, so consumers must not exercise async list I/O on Android.

Test signals: link success is the main signal; runtime use should be considered a failure unless a test deliberately expects abort.
