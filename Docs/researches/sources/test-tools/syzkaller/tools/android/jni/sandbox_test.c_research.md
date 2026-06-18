## sources/test-tools/syzkaller/tools/android/jni/sandbox_test.c

This C helper tests syzkaller's Android untrusted-app sandbox setup. It defines executor configuration macros, simple `fail/error/debug` logging macros, `doexit`, a `loop` function that runs `id`, a temp-directory setup, includes `executor/common_linux.h`, and calls `do_sandbox_android_untrusted_app()` from `main`.

Runtime flow creates a writable temporary directory under `/data/data/syzkaller` for untrusted-app mode, chmods/chdirs into it, then enters the executor sandbox helper. Dependencies are Android libc/syscalls, syzkaller executor common code, and the expected `/data/data/syzkaller` location. Risks include permission assumptions on device, `chmod 0777`, and no explicit return after sandbox call. It is built/run by the Android Makefile rather than unit-tested.
