<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mount/mount03_suid_child.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mount/mount03_suid_child.c

## Purpose
This file setuid helper used by mount03 to prove MS_NOSUID prevents privilege gain.
The source-level description states or implies: Copyright (c) Wipro Technologies Ltd, 2002. All Rights Reserved. Copyright (c) 2022 Petr Vorel <pvorel@suse.cz>

## Important APIs, Types, and Functions
Key local functions: `main()`.
Primary syscall/API surface: `mount`.
LTP and helper APIs used include: `TST_EXP_FAIL`, `setreuid`, `tst_reinit`, `tst_test`.

## Control Flow
This legacy LTP test parses options with `tst_parse_opts`, calls `setup()`, loops with `TEST_LOOPING(lc)`, invokes the syscall or regression action, checks `TEST_RETURN`/`TEST_ERRNO` or child status, then calls `cleanup()` and `tst_exit()`.

## State and Persistence
Persistent or externally visible state includes mount namespace, mounted filesystems, and mount flags; effective uid changes between root and nobody. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `mount` syscall test directory. LTP device formatting/mountpoint support, root privileges, filesystem skip lists, statfs/statvfs, and helper resource files.

## Risks
Risks: requires privilege and may produce misleading failures if user switching or capability assumptions differ; mount and filesystem coverage can vary by kernel, filesystem support, and cleanup ordering; bad-address tests may differ between libc wrappers and raw syscalls.

## Test Signals
negative paths validate exact errno or unexpected-success handling.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mount/mount03_suid_child.c -->
