## sources/test-tools/syzkaller/tools/android/jni/Android.mk

This Android NDK makefile defines the `sandbox_test` executable module from `sandbox_test.c` and includes headers from `../../`, which lets it include syzkaller executor common code.

It integrates with the parent Android Makefile and NDK build system. Risks are minimal: include-path drift and reliance on NDK executable build support for the selected ABI.
