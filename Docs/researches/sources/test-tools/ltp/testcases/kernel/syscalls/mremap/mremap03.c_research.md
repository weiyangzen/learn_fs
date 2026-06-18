<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mremap/mremap03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mremap/mremap03.c

## Purpose
This file legacy negative mremap test for an unmapped old region expecting EFAULT.
The source-level description states or implies: Copyright (c) International Business Machines Corp., 2001 This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warrant

## Important APIs, Types, and Functions
Key local functions: `setup()`, `cleanup()`, `main()`, `setup()`, `cleanup()`.
Primary syscall/API surface: `munmap`, `mremap`.
LTP and helper APIs used include: `mremap`, `munmap`, `tst_brkm`, `tst_count`, `tst_exit`, `tst_get_bad_addr`, `tst_parse_opts`, `tst_resm`, `tst_sig`.

## Control Flow
This legacy LTP test parses options with `tst_parse_opts`, calls `setup()`, loops with `TEST_LOOPING(lc)`, invokes the syscall or regression action, checks `TEST_RETURN`/`TEST_ERRNO` or child status, then calls `cleanup()` and `tst_exit()`.

## State and Persistence
Persistent or externally visible state includes virtual memory mappings and page/accounting state; child/thread synchronization and signal-observed outcomes. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `mremap` syscall test directory. mmap/mremap semantics, SysV IPC for mremap04, file-backed mappings, userfaultfd for mremap07, pthreads where needed, and kernel regression tags.

## Risks
Risks: signal or child-process expectations can be timing-sensitive; bad-address tests may differ between libc wrappers and raw syscalls.

## Test Signals
explicit TPASS/TST_EXP_PASS checks mark expected syscall behavior; negative paths validate exact errno or unexpected-success handling.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mremap/mremap03.c -->
