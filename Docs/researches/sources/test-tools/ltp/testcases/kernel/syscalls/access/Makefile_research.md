# sources/test-tools/ltp/testcases/kernel/syscalls/access/Makefile

Purpose: LTP leaf Makefile for `access()` syscall tests. It includes the standard testcase and generic leaf makefiles with no custom compiler or linker settings. Runtime root, fork, tmpdir, read-only filesystem, and buffer needs are declared in individual C tests. State is build-only. Risk is low and limited to LTP make infrastructure. Test signal is successful compilation of `access01` through `access04`.
