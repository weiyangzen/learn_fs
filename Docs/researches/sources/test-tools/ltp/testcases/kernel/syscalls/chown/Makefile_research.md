# sources/test-tools/ltp/testcases/kernel/syscalls/chown/Makefile

Purpose: LTP leaf Makefile for `chown()` tests. It includes standard testcase rules, `../utils/compat_16.mk` for 16-bit uid/gid compatibility wrappers, and generic leaf targets. Runtime root/tmpdir/rofs requirements are declared in C files. State is build-only. Dependency risk is the compatibility make include and generated `CHOWN` wrapper. Test signal is successful compilation of all chown tests.
