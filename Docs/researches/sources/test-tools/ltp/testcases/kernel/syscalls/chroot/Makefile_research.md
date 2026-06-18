# sources/test-tools/ltp/testcases/kernel/syscalls/chroot/Makefile

Purpose: LTP leaf Makefile for `chroot()` tests. It includes standard testcase and generic leaf target makefiles without custom flags. Runtime root/tmpdir/fork requirements are in the C files. State is build-only. Risks are minimal. Test signal is successful build of all chroot tests.
