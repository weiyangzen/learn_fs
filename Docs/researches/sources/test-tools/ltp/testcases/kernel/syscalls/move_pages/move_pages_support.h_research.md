<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/move_pages/move_pages_support.h -->
# sources/test-tools/ltp/testcases/kernel/syscalls/move_pages/move_pages_support.h

## Purpose
This file declares the NUMA helper API used by the move_pages syscall tests.
The source-level description states or implies: Copyright (c) 2008 Vijay Kumar B. <vijaykumar@bravegnu.org> This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warra

## Important APIs, Types, and Functions
Key local functions: `get_page_size()`, `free_pages()`, `alloc_pages_on_nodes()`, `alloc_pages_linear()`, `alloc_pages_on_node()`, `verify_pages_on_nodes()`, `verify_pages_linear()`, `verify_pages_on_node()`, `alloc_shared_pages_on_node()`, `free_shared_pages()`, `free_sem()`, `check_config()`.
LTP and helper APIs used include: `numa_helper`.

## Control Flow
This legacy LTP test parses options with `tst_parse_opts`, calls `setup()`, loops with `TEST_LOOPING(lc)`, invokes the syscall or regression action, checks `TEST_RETURN`/`TEST_ERRNO` or child status, then calls `cleanup()` and `tst_exit()`.

## State and Persistence
Persistent or externally visible state includes NUMA placement, page migration status, or hugepage sysfs settings; child/thread synchronization and signal-observed outcomes. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `move_pages` syscall test directory. libnuma/numaif, LTP NUMA helpers, allowed memory node discovery, root or nobody credentials for permission tests, and shared semaphore synchronization.

## Risks
Risks: main risk is environment-specific syscall behavior causing TCONF or errno differences rather than source-level state corruption.

## Test Signals
.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/move_pages/move_pages_support.h -->
