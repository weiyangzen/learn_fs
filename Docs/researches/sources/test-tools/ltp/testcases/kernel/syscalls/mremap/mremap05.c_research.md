<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mremap/mremap05.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mremap/mremap05.c

## Purpose
This file MREMAP_FIXED matrix for missing MAYMOVE, unaligned target, overlapping ranges, moving data, and replacing an existing target mapping.
The source-level description states or implies: Copyright (C) 2012 Linux Test Project, Inc. This program is free software; you can redistribute it and/or modify it under the terms of version 2 of the GNU General Public License as published by the Free Software Foundation. This program is distributed in the hope that it would be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. Further, this

## Important APIs, Types, and Functions
Key local functions: `setup()`, `cleanup()`, `setup0()`, `setup1()`, `setup2()`, `setup3()`, `setup4()`, `cleanup0()`, `cleanup1()`, `free_test_area()`, `test_mremap()`, `setup0()`, `setup1()`, `setup2()`, `setup3()`, `setup4()`, `cleanup0()`, `cleanup1()`.
Primary syscall/API surface: `mmap`, `mremap`.
LTP and helper APIs used include: `SAFE_MUNMAP`, `mmap`, `mremap`, `tst_brkm`, `tst_count`, `tst_exit`, `tst_parse_opts`, `tst_resm`.
Harness fields present in `struct tst_test`: `.cleanup`, `.setup`.

## Control Flow
This legacy LTP test parses options with `tst_parse_opts`, calls `setup()`, loops with `TEST_LOOPING(lc)`, invokes the syscall or regression action, checks `TEST_RETURN`/`TEST_ERRNO` or child status, then calls `cleanup()` and `tst_exit()`.

## State and Persistence
Persistent or externally visible state includes virtual memory mappings and page/accounting state. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `mremap` syscall test directory. mmap/mremap semantics, SysV IPC for mremap04, file-backed mappings, userfaultfd for mremap07, pthreads where needed, and kernel regression tags.

## Risks
Risks: main risk is environment-specific syscall behavior causing TCONF or errno differences rather than source-level state corruption.

## Test Signals
explicit TPASS/TST_EXP_PASS checks mark expected syscall behavior; negative paths validate exact errno or unexpected-success handling.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mremap/mremap05.c -->
