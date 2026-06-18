# sources/test-tools/ltp/testcases/kernel/syscalls/chdir/Makefile

Purpose: LTP leaf Makefile for `chdir()` tests. It includes standard testcase and generic leaf target makefiles without custom flags. Runtime mount, root, tmpdir, and buffer needs are declared in C sources. State is build-only. Risks are minimal. Test signal is successful build of the chdir test binaries.
