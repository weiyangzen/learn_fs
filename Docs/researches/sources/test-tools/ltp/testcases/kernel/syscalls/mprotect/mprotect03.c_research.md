<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mprotect/mprotect03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mprotect/mprotect03.c

## Purpose
This file checks mprotect can remove write permission from a shared mapping and cause child writes to SIGSEGV.
The source-level description states or implies: Copyright (c) International Business Machines Corp., 2001 This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warrant

## Important APIs, Types, and Functions
Key local functions: `cleanup()`, `setup()`, `main()`, `sighandler()`, `setup()`, `cleanup()`.
Primary syscall/API surface: `mmap`, `mprotect`.
LTP and helper APIs used include: `SAFE_CLOSE`, `SAFE_MUNMAP`, `SAFE_UNLINK`, `SAFE_WRITE`, `SAFE_WRITE_ALL`, `TEST`, `fork`, `mmap`, `mprotect`, `tst_brkm`, `tst_count`, `tst_exit`, `tst_fork`, `tst_parse_opts`, `tst_resm`, `tst_rmdir`, `tst_sig`, `tst_tmpdir`.

## Control Flow
This legacy LTP test parses options with `tst_parse_opts`, calls `setup()`, loops with `TEST_LOOPING(lc)`, invokes the syscall or regression action, checks `TEST_RETURN`/`TEST_ERRNO` or child status, then calls `cleanup()` and `tst_exit()`.

## State and Persistence
Persistent or externally visible state includes virtual memory mappings and page/accounting state; child/thread synchronization and signal-observed outcomes; temporary files, file descriptors, or LTP temp directories. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `mprotect` syscall test directory. mmap/mprotect primitives, legacy LTP signal handling or new harness tags, child processes for SIGSEGV checks, and architecture/compiler cache support in executable tests.

## Risks
Risks: signal or child-process expectations can be timing-sensitive.

## Test Signals
explicit TPASS/TST_EXP_PASS checks mark expected syscall behavior; negative paths validate exact errno or unexpected-success handling; child exit status or signal delivery is part of pass/fail evidence.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mprotect/mprotect03.c -->
