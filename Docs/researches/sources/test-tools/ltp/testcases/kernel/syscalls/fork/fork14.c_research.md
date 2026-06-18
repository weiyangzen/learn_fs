<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fork/fork14.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fork/fork14.c

Purpose: Additional fork regression coverage for high process counts or VM/resource inheritance. Source notes: \ This test is a reproducer for kernel 3.5: 7edc8b0ac16c ("mm/fork: fix overflow in vma length when copying mmap on clone") Since VMA length in dup_mmap() is calculated and stored in a unsigned int, it will overflow when length of mmaped memory > 16 TB. When overflow occurs, fork will incorrectly succeed. The patch above fixed it. keep track of the failed fork() and verify that next one is failing as well. SPDX-License-Identifier: GPL-2.0-only The file was read in full for this report (122 lines, 2343 bytes).

Important APIs/types/functions: calls/wrappers: fork(), mmap(), SAFE_MUNMAP, SAFE_MALLOC; types/structs: struct tst_test, struct tst_tag; functions: run, setup, cleanup; local macros/constants: LARGE, EXTENT.

Control flow: setup path: setup; exercise path: run; cleanup path: cleanup.

State and persistence behavior: The test manipulates child processes and wait status, shared or anonymous memory mappings. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `tst_test.h`, `stdlib.h`, `sys/wait.h`; integrates with the LTP fork syscall suite; uses the LTP C harness and result macros.

Risks: scheduler timing and signal ordering can make failures hard to diagnose.

Test signals: explicit pass reporting; explicit failure reporting; errno checks: EXTENT, ECHILD; harness metadata: .test_all, .setup, .cleanup, .forks_child, .needs_abi_bits, .tags.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fork/fork14.c -->
