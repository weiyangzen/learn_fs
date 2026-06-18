## sources/test-tools/syzkaller/tools/android/Makefile

This Makefile builds and runs the Android sandbox test helper. Target `libs/arm64-v8a/sandbox_test` depends on `jni/sandbox_test.c` and invokes `ndk-build`. `push` uploads the built binary to `/data/local/tmp`, `run` pushes then executes it through adb, and `clean` removes NDK output directories.

State is local build artifacts plus device-side copied binary. Integration is with Android NDK, adb, and the JNI makefiles. Risks include assuming arm64 ABI, adb device availability, and not declaring `clean` in `.PHONY` despite declaring `all push run`.
