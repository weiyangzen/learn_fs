<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mount/mount04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mount/mount04.c

## Purpose
This file verifies mount(2) fails with EPERM after dropping effective uid to nobody.
The source-level description states or implies: Verify that mount(2) returns -1 and sets errno to EPERM if the user is not root.

## Important APIs, Types, and Functions
Key local functions: `cleanup()`, `run()`.
Primary syscall/API surface: `mount`.
LTP and helper APIs used include: `SAFE_GETPWNAM`, `SAFE_SETEUID`, `SAFE_UMOUNT`, `TST_EXP_FAIL`, `tst_device`, `tst_is_mounted`, `tst_test`.
Harness fields present in `struct tst_test`: `.cleanup`, `.format_device`, `.mntpoint`, `.needs_root`, `.test_all`.

## Control Flow
The modern LTP harness enters through `.test_all` after optional `.setup`; it runs one case or iterates `.tcnt` table entries, records results with `tst_res`/`TST_EXP_*`, and then invokes `.cleanup` for mapped memory, descriptors, mounts, queues, or credentials.
The file contains table-driven state, with roughly 1 initializer blocks controlling argument combinations, expected errnos, flags, or variants.

## State and Persistence
Persistent or externally visible state includes mount namespace, mounted filesystems, and mount flags; effective uid changes between root and nobody. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `mount` syscall test directory. LTP device formatting/mountpoint support, root privileges, filesystem skip lists, statfs/statvfs, and helper resource files.

## Risks
Risks: requires privilege and may produce misleading failures if user switching or capability assumptions differ; mount and filesystem coverage can vary by kernel, filesystem support, and cleanup ordering.

## Test Signals
negative paths validate exact errno or unexpected-success handling.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mount/mount04.c -->
