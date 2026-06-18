<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/modify_ldt/common.h -->
# sources/test-tools/ltp/testcases/kernel/syscalls/modify_ldt/common.h

## Purpose
This file provides the modify_ldt helper that fills a user_desc entry and installs it with SAFE_MODIFY_LDT.
The source-level description states or implies: Copyright (c) International Business Machines Corp., 2001 07/2001 Ported by Wayne Boyer Copyright (c) 2025 SUSE LLC Ricardo B. Marlière <rbm@suse.com>

## Important APIs, Types, and Functions
LTP and helper APIs used include: `SAFE_MODIFY_LDT`, `tst_test`.

## Control Flow
This legacy LTP test parses options with `tst_parse_opts`, calls `setup()`, loops with `TEST_LOOPING(lc)`, invokes the syscall or regression action, checks `TEST_RETURN`/`TEST_ERRNO` or child status, then calls `cleanup()` and `tst_exit()`.

## State and Persistence
Persistent or externally visible state includes . Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `modify_ldt` syscall test directory. x86/i386 LDT ABI via lapi/ldt.h and SAFE_MODIFY_LDT; tests are architecture-gated.

## Risks
Risks: main risk is environment-specific syscall behavior causing TCONF or errno differences rather than source-level state corruption.

## Test Signals
.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/modify_ldt/common.h -->
