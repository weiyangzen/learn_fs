# sources/test-tools/ltp/testcases/kernel/syscalls/cachestat/Makefile

Purpose: LTP leaf Makefile for Linux `cachestat()` tests. It includes standard testcase rules, links `-lrt`, and delegates to the generic leaf target. Runtime filesystem mounts, hugetlbfs, and descriptor iteration are declared in C files. State is build-only. Dependencies are LTP lapi support for modern `cachestat` and realtime library. Risks are syscall/header availability on older systems. Test signal is successful build of the cachestat suite.
