<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/move_mount/move_mount03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/move_mount/move_mount03.c

## Purpose
This file kernel 6.5 MOVE_MOUNT_BENEATH regression test that stacks one tmpfs mount below another and checks visibility after unmount.
The source-level description states or implies: Test allow to mount beneath top mount feature added in kernel 6.5: 6ac392815628 ("fs: allow to mount beneath top mount") Test based on: https://github.com/brauner/move-mount-beneath See also: - https://lore.kernel.org/all/20230202-fs-move-mount-replace-v4-0-98f3d80d7eaa@kernel.org/ - https://lwn.net/Articles/930591/ - https://github.com/brauner/move-mount-beneath

## Important APIs, Types, and Functions
Key local functions: `run()`, `setup()`, `cleanup()`.
Primary syscall/API surface: `mount`, `move_mount`, `open_tree`, `fsmount`.
LTP and helper APIs used include: `SAFE_CLOSE`, `SAFE_MKDIR`, `SAFE_MOUNT`, `SAFE_OPEN`, `SAFE_TOUCH`, `SAFE_UMOUNT`, `TST_EXP_FAIL`, `TST_EXP_PASS`, `fsmount`, `move_mount`, `open_tree`, `tst_brk`, `tst_is_mounted_at_tmpdir`, `tst_tag`, `tst_test`.
Harness fields present in `struct tst_test`: `.cleanup`, `.min_kver`, `.needs_root`, `.needs_tmpdir`, `.setup`, `.tags`, `.test_all`.

## Control Flow
The modern LTP harness enters through `.test_all` after optional `.setup`; it runs one case or iterates `.tcnt` table entries, records results with `tst_res`/`TST_EXP_*`, and then invokes `.cleanup` for mapped memory, descriptors, mounts, queues, or credentials.
The file contains table-driven state, with roughly 3 initializer blocks controlling argument combinations, expected errnos, flags, or variants.

## State and Persistence
Persistent or externally visible state includes mount namespace, mounted filesystems, and mount flags; temporary files, file descriptors, or LTP temp directories. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `move_mount` syscall test directory. new mount API wrappers fsopen/fsconfig/fsmount/open_tree/move_mount, root privileges, formatted devices, tmpfs, and kernel-version gates.
The test declares a minimum kernel version so unsupported kernels are filtered by the harness.
Regression tags link the scenario to upstream commits or CVEs, which are useful signals when triaging failures.

## Risks
Risks: requires privilege and may produce misleading failures if user switching or capability assumptions differ; mount and filesystem coverage can vary by kernel, filesystem support, and cleanup ordering.

## Test Signals
explicit TPASS/TST_EXP_PASS checks mark expected syscall behavior; negative paths validate exact errno or unexpected-success handling.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/move_mount/move_mount03.c -->
