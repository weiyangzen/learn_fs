<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mlock2/mlock203.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mlock2/mlock203.c

## Purpose
This file regression-checks that relocking an MLOCK_ONFAULT range with normal mlock2 accounting does not double-count VmLck.
The source-level description states or implies: Copyright (c) 2018 FUJITSU LIMITED. All rights reserved. Author: Xiao Yang <yangx.jy@cn.fujitsu.com>

## Important APIs, Types, and Functions
Key local functions: `verify_mlock2()`, `setup()`, `cleanup()`.
Primary syscall/API surface: `mlock2`.
LTP and helper APIs used include: `SAFE_FILE_LINES_SCANF`, `SAFE_MMAP`, `SAFE_MUNLOCK`, `SAFE_MUNMAP`, `TEST`, `mlock`, `mlock2`, `tst_res`, `tst_syscall`, `tst_test`.
Harness fields present in `struct tst_test`: `.cleanup`, `.needs_root`, `.setup`, `.test_all`.

## Control Flow
The modern LTP harness enters through `.test_all` after optional `.setup`; it runs one case or iterates `.tcnt` table entries, records results with `tst_res`/`TST_EXP_*`, and then invokes `.cleanup` for mapped memory, descriptors, mounts, queues, or credentials.
The file contains table-driven state, with roughly 1 initializer blocks controlling argument combinations, expected errnos, flags, or variants.

## State and Persistence
Persistent or externally visible state includes virtual memory mappings and page/accounting state; temporary files, file descriptors, or LTP temp directories. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `mlock2` syscall test directory. LTP new harness, lapi/syscalls, Linux mlock2 definitions, /proc/self/status VmLck, RLIMIT_MEMLOCK, root/nobody credential changes.

## Risks
Risks: requires privilege and may produce misleading failures if user switching or capability assumptions differ.

## Test Signals
explicit TPASS/TST_EXP_PASS checks mark expected syscall behavior; negative paths validate exact errno or unexpected-success handling; TCONF is used for unsupported kernel, architecture, NUMA, filesystem, cgroup, or feature conditions; kernel-visible accounting files or status APIs are read back to verify effects.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mlock2/mlock203.c -->
