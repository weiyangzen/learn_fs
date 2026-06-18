<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mount_setattr/mount_setattr01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mount_setattr/mount_setattr01.c

## Purpose
This file checks mount_setattr and open_tree_attr variants by setting mount attributes and observing statvfs flags after move_mount.
The source-level description states or implies: Basic mount_setattr()/open_tree_attr() test. Test whether the basic mount attributes are set correctly. Verify some MOUNT_SETATTR(2) attributes: - MOUNT_ATTR_RDONLY - makes the mount read-only - MOUNT_ATTR_NOSUID - causes the mount not to honor the set-user-ID and set-group-ID mode bits and file capabilities when executing programs. - MOUNT_ATTR_NODEV - prevents access to devices on this mount - MOUNT_ATTR_NOEXEC - p

## Important APIs, Types, and Functions
Key local functions: `open_tree_variant1()`, `open_tree_variant2()`, `cleanup()`, `setup()`, `open_tree_variant1()`, `open_tree_variant2()`, `run()`.
Primary syscall/API surface: `mount`, `mount_setattr`, `move_mount`, `open_tree`, `open_tree_attr`, `fsmount`.
LTP and helper APIs used include: `SAFE_CLOSE`, `SAFE_MKDIR`, `SAFE_UMOUNT`, `TST_EXP_FD`, `TST_EXP_FD_SILENT`, `TST_EXP_PASS`, `TST_EXP_PASS_SILENT`, `fsmount`, `mount_setattr`, `move_mount`, `open_tree`, `open_tree_attr`, `tst_buffers`, `tst_res`, `tst_test`, `tst_variant`.
Harness fields present in `struct tst_test`: `.all_filesystems`, `.bufs`, `.cleanup`, `.mntpoint`, `.mount_device`, `.needs_root`, `.setup`, `.skip_filesystems`, `.tcnt`, `.test`, `.test_variants`.

## Control Flow
The modern LTP harness enters through `.test` after optional `.setup`; it runs one case or iterates `.tcnt` table entries, records results with `tst_res`/`TST_EXP_*`, and then invokes `.cleanup` for mapped memory, descriptors, mounts, queues, or credentials.
The file contains table-driven state, with roughly 5 initializer blocks controlling argument combinations, expected errnos, flags, or variants.

## State and Persistence
Persistent or externally visible state includes mount namespace, mounted filesystems, and mount flags; temporary files, file descriptors, or LTP temp directories. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `mount_setattr` syscall test directory. new mount API wrappers from lapi/fsmount.h, root privileges, mount namespaces, open_tree/move_mount, and statvfs or mountinfo inspection.

## Risks
Risks: requires privilege and may produce misleading failures if user switching or capability assumptions differ; mount and filesystem coverage can vary by kernel, filesystem support, and cleanup ordering.

## Test Signals
explicit TPASS/TST_EXP_PASS checks mark expected syscall behavior; negative paths validate exact errno or unexpected-success handling; kernel-visible accounting files or status APIs are read back to verify effects.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mount_setattr/mount_setattr01.c -->
