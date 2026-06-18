# sources/test-tools/ltp/testcases/kernel/syscalls/accept/Makefile

Purpose: LTP leaf Makefile for `accept()` tests. It includes the standard LTP testcase and leaf target makefiles, and adds `-pthread` only for `accept02`, which uses server/client pthreads and checkpoints. Runtime socket setup is in the C files. State is build-only. Dependencies are pthread support for the CVE regression test. Risk is missing the target-specific flag causing unresolved pthread symbols. Test signal is successful build of `accept01`, `accept02`, and `accept03`.
