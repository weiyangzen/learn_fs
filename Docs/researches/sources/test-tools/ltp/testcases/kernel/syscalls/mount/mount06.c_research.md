<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mount/mount06.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mount/mount06.c

## Purpose
This file tests MS_MOVE by moving a mounted filesystem from one mountpoint to another in a private mount parent.
The source-level description states or implies: Test for feature MS_MOVE of mount, which moves an existing mount point to a new location.

## Important APIs, Types, and Functions
Key local functions: `setup()`, `cleanup()`, `run()`.
Primary syscall/API surface: `mount`.
LTP and helper APIs used include: `SAFE_FILE_PRINTF`, `SAFE_MKDIR`, `SAFE_MOUNT`, `SAFE_RMDIR`, `SAFE_UMOUNT`, `TEST`, `TST_EXP_FAIL`, `TST_EXP_PASS`, `tst_device`, `tst_is_mounted`, `tst_test`, `tst_tmpdir_genpath`, `tst_tmpdir_path`.
Harness fields present in `struct tst_test`: `.all_filesystems`, `.cleanup`, `.format_device`, `.mntpoint`, `.needs_root`, `.setup`, `.skip_filesystems`, `.test_all`.

## Control Flow
The modern LTP harness enters through `.test_all` after optional `.setup`; it runs one case or iterates `.tcnt` table entries, records results with `tst_res`/`TST_EXP_*`, and then invokes `.cleanup` for mapped memory, descriptors, mounts, queues, or credentials.
The file contains table-driven state, with roughly 2 initializer blocks controlling argument combinations, expected errnos, flags, or variants.

## State and Persistence
Persistent or externally visible state includes mount namespace, mounted filesystems, and mount flags; temporary files, file descriptors, or LTP temp directories. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `mount` syscall test directory. LTP device formatting/mountpoint support, root privileges, filesystem skip lists, statfs/statvfs, and helper resource files.

## Risks
Risks: requires privilege and may produce misleading failures if user switching or capability assumptions differ; mount and filesystem coverage can vary by kernel, filesystem support, and cleanup ordering.

## Test Signals
explicit TPASS/TST_EXP_PASS checks mark expected syscall behavior; negative paths validate exact errno or unexpected-success handling.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mount/mount06.c -->
