<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mlockall/mlockall01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mlockall/mlockall01.c

## Purpose
This file legacy positive mlockall(2) smoke test for MCL_CURRENT, MCL_FUTURE, and their combination under root.
The source-level description states or implies: Copyright (c) Wipro Technologies Ltd, 2002. All Rights Reserved. This program is free software; you can redistribute it and/or modify it under the terms of version 2 of the GNU General Public License as published by the Free Software Foundation. This program is distributed in the hope that it would be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PU

## Important APIs, Types, and Functions
Key local functions: `setup()`, `cleanup()`, `main()`, `setup()`, `cleanup()`.
Primary syscall/API surface: `mlockall`.
LTP and helper APIs used include: `TEST`, `mlockall`, `tst_count`, `tst_exit`, `tst_parse_opts`, `tst_require_root`, `tst_resm`, `tst_sig`.

## Control Flow
This legacy LTP test parses options with `tst_parse_opts`, calls `setup()`, loops with `TEST_LOOPING(lc)`, invokes the syscall or regression action, checks `TEST_RETURN`/`TEST_ERRNO` or child status, then calls `cleanup()` and `tst_exit()`.

## State and Persistence
Persistent or externally visible state includes virtual memory mappings and page/accounting state; child/thread synchronization and signal-observed outcomes; temporary files, file descriptors, or LTP temp directories. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `mlockall` syscall test directory. legacy LTP harness test.h, mlockall(2), RLIMIT_MEMLOCK, root/nobody credential transitions, and loop/pause options.

## Risks
Risks: requires privilege and may produce misleading failures if user switching or capability assumptions differ; signal or child-process expectations can be timing-sensitive.

## Test Signals
explicit TPASS/TST_EXP_PASS checks mark expected syscall behavior; negative paths validate exact errno or unexpected-success handling.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mlockall/mlockall01.c -->
