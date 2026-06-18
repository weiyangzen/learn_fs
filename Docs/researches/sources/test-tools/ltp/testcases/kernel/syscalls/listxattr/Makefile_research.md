# sources/test-tools/ltp/testcases/kernel/syscalls/listxattr/Makefile

Purpose: builds `listxattr` tests. It includes standard LTP testcase rules, adds `$(ACL_LIBS)` only for `listxattr04` outside this subset, and delegates to generic leaf targets. The two files in this work item need no extra libraries but depend on xattr headers at compile time. Runtime feature checks live in the C files. Risks are missing ACL libs affecting adjacent targets and missing xattr headers yielding TCONF code paths. Test signal is successful build.
