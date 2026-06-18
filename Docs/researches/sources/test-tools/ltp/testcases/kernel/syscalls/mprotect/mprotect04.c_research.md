<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mprotect/mprotect04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mprotect/mprotect04.c

## Purpose
This file tests PROT_NONE faulting and PROT_EXEC execution after copying a function to an anonymous page.
The source-level description states or implies: Copyright (c) 2014 Fujitsu Ltd. Author: Xing Gu <gux.fnst@cn.fujitsu.com> This program is free software; you can redistribute it and/or modify it under the terms of version 2 of the GNU General Public License as published by the Free Software Foundation. This program is distributed in the hope that it would be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PART

## Important APIs, Types, and Functions
Key local functions: `sighandler()`, `setup()`, `cleanup()`, `testfunc_protnone()`, `testfunc_protexec()`, `main()`, `sighandler()`, `setup()`, `testfunc_protnone()`, `exec_func()`, `page_present()`, `clear_cache()`, `testfunc_protexec()`, `cleanup()`.
Primary syscall/API surface: `mprotect`.
LTP and helper APIs used include: `SAFE_CLOSE`, `SAFE_MMAP`, `SAFE_MUNMAP`, `SAFE_OPEN`, `TEST`, `mprotect`, `tst_brkm`, `tst_count`, `tst_exit`, `tst_parse_opts`, `tst_resm`, `tst_rmdir`, `tst_sig`, `tst_tmpdir`.

## Control Flow
This legacy LTP test parses options with `tst_parse_opts`, calls `setup()`, loops with `TEST_LOOPING(lc)`, invokes the syscall or regression action, checks `TEST_RETURN`/`TEST_ERRNO` or child status, then calls `cleanup()` and `tst_exit()`.

## State and Persistence
Persistent or externally visible state includes virtual memory mappings and page/accounting state; child/thread synchronization and signal-observed outcomes; temporary files, file descriptors, or LTP temp directories. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `mprotect` syscall test directory. mmap/mprotect primitives, legacy LTP signal handling or new harness tags, child processes for SIGSEGV checks, and architecture/compiler cache support in executable tests.

## Risks
Risks: signal or child-process expectations can be timing-sensitive; bad-address tests may differ between libc wrappers and raw syscalls.

## Test Signals
explicit TPASS/TST_EXP_PASS checks mark expected syscall behavior; negative paths validate exact errno or unexpected-success handling; TCONF is used for unsupported kernel, architecture, NUMA, filesystem, cgroup, or feature conditions; child exit status or signal delivery is part of pass/fail evidence.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mprotect/mprotect04.c -->
