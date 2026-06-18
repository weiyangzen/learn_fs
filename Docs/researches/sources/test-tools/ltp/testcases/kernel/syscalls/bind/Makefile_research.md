# sources/test-tools/ltp/testcases/kernel/syscalls/bind/Makefile

Purpose: LTP leaf Makefile for `bind()` tests. It includes standard testcase rules, adds `-pthread` to `bind04`, `bind05`, and `bind06`, and links `bind06` with `-lrt` for fuzzy sync/timing support. Runtime protocol, namespace, and filesystem requirements are declared in C files. State is build-only. Dependencies are pthreads and realtime library for selected tests. Risk is missing target-specific flags causing link failures. Test signal is successful build of all bind tests and shared header consumers.
