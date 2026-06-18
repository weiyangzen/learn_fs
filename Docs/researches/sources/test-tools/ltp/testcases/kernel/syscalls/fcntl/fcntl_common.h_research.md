<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl_common.h -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl_common.h

Purpose: Shared helpers and constants for fcntl OFD-lock concurrency tests, including file names, buffer sizes, and common record geometry. Source notes: F_OFD_* commands always require flock64 struct. Older GLibc (pre 2.29) would pass the flock sturct directly to the kernel even if it had 32-bit offsets. If we are on 32-bit abi we need to use the fcntl64 compat syscall. See: glibc: 06ab719d30 Fix Linux fcntl OFD locks for non-LFS architectures (BZ#20251) kernel: fs/fcntl.c FCNTL_COMMON_H__ The file was read in full for this report (75 lines, 1661 bytes).

Important APIs/types/functions: calls/wrappers: SAFE_FCNTL; types/structs: struct my_flock64, struct flock; functions: fcntl_compat; local macros/constants: FCNTL_COMMON_H__, FCNTL_COMPAT.

Control flow: the file provides declarations/helpers consumed by sibling tests.

State and persistence behavior: The test manipulates advisory locks or file leases. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `inttypes.h`, `tst_test.h`, `tst_kernel.h`, `lapi/syscalls.h`, `lapi/abisize.h`, `lapi/fcntl.h`; integrates with the LTP fcntl syscall suite; uses the LTP C harness and result macros; uses LTP Linux API compatibility headers.

Risks: expected errno/return-value assertions are sensitive to kernel and libc behavior.

Test signals: key constants: F_OFD_, __NR_fcntl64.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl_common.h -->
