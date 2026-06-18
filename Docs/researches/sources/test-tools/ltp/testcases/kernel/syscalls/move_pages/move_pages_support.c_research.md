<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/move_pages/move_pages_support.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/move_pages/move_pages_support.c

## Purpose
This file shared NUMA helper implementation for page allocation, NUMA status verification, shared page setup, semaphores, and config gating.
The source-level description states or implies: Copyright (c) 2008 Vijay Kumar B. <vijaykumar@bravegnu.org> This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warra

## Important APIs, Types, and Functions
Key local functions: `get_page_size()`, `free_pages()`, `alloc_pages_on_nodes()`, `alloc_pages_linear()`, `alloc_pages_on_node()`, `verify_pages_on_nodes()`, `verify_pages_linear()`, `verify_pages_on_node()`, `alloc_shared_pages_on_node()`, `free_shared_pages()`, `free_sem()`, `check_config()`.
Primary syscall/API surface: `mmap`, `munmap`.
LTP and helper APIs used include: `get_mempolicy`, `mmap`, `munmap`, `numa_alloc_onnode`, `numa_available`, `numa_free`, `numa_tonode_memory`, `tst_brkm`, `tst_resm`.

## Control Flow
This legacy LTP test parses options with `tst_parse_opts`, calls `setup()`, loops with `TEST_LOOPING(lc)`, invokes the syscall or regression action, checks `TEST_RETURN`/`TEST_ERRNO` or child status, then calls `cleanup()` and `tst_exit()`.

## State and Persistence
Persistent or externally visible state includes virtual memory mappings and page/accounting state; NUMA placement, page migration status, or hugepage sysfs settings; child/thread synchronization and signal-observed outcomes; temporary files, file descriptors, or LTP temp directories. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `move_pages` syscall test directory. libnuma/numaif, LTP NUMA helpers, allowed memory node discovery, root or nobody credentials for permission tests, and shared semaphore synchronization.
NUMA availability is compile/runtime gated; without libnuma or enough allowed memory nodes the expected result is TCONF rather than failure.

## Risks
Risks: main risk is environment-specific syscall behavior causing TCONF or errno differences rather than source-level state corruption.

## Test Signals
explicit TPASS/TST_EXP_PASS checks mark expected syscall behavior; negative paths validate exact errno or unexpected-success handling; TCONF is used for unsupported kernel, architecture, NUMA, filesystem, cgroup, or feature conditions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/move_pages/move_pages_support.c -->
