<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mount_setattr/mount_setattr02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mount_setattr/mount_setattr02.c

## Purpose
This file checks mount_attr.propagation handling for invalid, unchanged, shared, slave, and private propagation values.
The source-level description states or implies: This test is checking if the propagation field of the mount_attr structure is handled properly. - EINVAL with propagation set to -1 - When propagation is set to 0 it's not changed - MS_SHARED turns propagation on - MS_SLAVE turns propagation off - MS_PRIVATE turns propagation off

## Important APIs, Types, and Functions
Key local functions: `check_mount_type()`, `cleanup()`, `setup()`, `run()`.
Primary syscall/API surface: `mount_setattr`, `fsmount`.
LTP and helper APIs used include: `SAFE_FOPEN`, `SAFE_MKDIR`, `SAFE_MOUNT`, `SAFE_UMOUNT`, `SAFE_UNSHARE`, `TST_EXP_EQ_LI`, `TST_EXP_FAIL_SILENT`, `TST_EXP_PASS_SILENT`, `fsmount`, `mount_setattr`, `tst_res`, `tst_safe_stdio`, `tst_test`, `tst_tmpdir_path`.
Harness fields present in `struct tst_test`: `.cleanup`, `.needs_root`, `.needs_tmpdir`, `.setup`, `.test_all`.

## Control Flow
The modern LTP harness enters through `.test_all` after optional `.setup`; it runs one case or iterates `.tcnt` table entries, records results with `tst_res`/`TST_EXP_*`, and then invokes `.cleanup` for mapped memory, descriptors, mounts, queues, or credentials.
The file contains table-driven state, with roughly 4 initializer blocks controlling argument combinations, expected errnos, flags, or variants.

## State and Persistence
Persistent or externally visible state includes mount namespace, mounted filesystems, and mount flags; temporary files, file descriptors, or LTP temp directories. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `mount_setattr` syscall test directory. new mount API wrappers from lapi/fsmount.h, root privileges, mount namespaces, open_tree/move_mount, and statvfs or mountinfo inspection.

## Risks
Risks: requires privilege and may produce misleading failures if user switching or capability assumptions differ; mount and filesystem coverage can vary by kernel, filesystem support, and cleanup ordering; It unshares the mount namespace and remounts / private; cleanup must not leak mounts in the namespace..

## Test Signals
explicit TPASS/TST_EXP_PASS checks mark expected syscall behavior; negative paths validate exact errno or unexpected-success handling; kernel-visible accounting files or status APIs are read back to verify effects.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mount_setattr/mount_setattr02.c -->
