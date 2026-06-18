# sources/test-tools/ltp/testcases/kernel/syscalls/listen/Makefile

Purpose: builds the `listen` syscall tests with standard LTP rules and generic leaf targets. It has no special libraries or runtime configuration. Integration points are old `test.h`, socket safe macros, and libc networking headers used by `listen01.c`. Risks are minimal build-path issues. Test signal is successful compilation of `listen01`.
