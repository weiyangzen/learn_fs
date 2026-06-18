<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/move_pages/move_pages09.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/move_pages/move_pages09.c

## Purpose
This file requests pages to stay on their current NUMA node and expects move_pages to succeed.
The source-level description states or implies: Copyright (c) 2008 Vijay Kumar B. <vijaykumar@bravegnu.org> Based on testcases/kernel/syscalls/waitpid/waitpid01.c Original copyright message: Copyright (c) International Business Machines Corp., 2001 This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option

## Important APIs, Types, and Functions
Key local functions: `setup()`, `cleanup()`, `main()`, `setup()`, `cleanup()`.
Primary syscall/API surface: `move_pages`.
LTP and helper APIs used include: `fork`, `numa_move_pages`, `tst_brkm`, `tst_count`, `tst_exit`, `tst_parse_opts`, `tst_resm`, `tst_sig`.

## Control Flow
This legacy LTP test parses options with `tst_parse_opts`, calls `setup()`, loops with `TEST_LOOPING(lc)`, invokes the syscall or regression action, checks `TEST_RETURN`/`TEST_ERRNO` or child status, then calls `cleanup()` and `tst_exit()`.

## State and Persistence
Persistent or externally visible state includes NUMA placement, page migration status, or hugepage sysfs settings; child/thread synchronization and signal-observed outcomes; temporary files, file descriptors, or LTP temp directories. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `move_pages` syscall test directory. libnuma/numaif, LTP NUMA helpers, allowed memory node discovery, root or nobody credentials for permission tests, and shared semaphore synchronization.
NUMA availability is compile/runtime gated; without libnuma or enough allowed memory nodes the expected result is TCONF rather than failure.

## Risks
Risks: signal or child-process expectations can be timing-sensitive.

## Test Signals
explicit TPASS/TST_EXP_PASS checks mark expected syscall behavior; negative paths validate exact errno or unexpected-success handling; TCONF is used for unsupported kernel, architecture, NUMA, filesystem, cgroup, or feature conditions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/move_pages/move_pages09.c -->
