<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/move_mount/move_mount02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/move_mount/move_mount02.c

## Purpose
This file negative move_mount(2) test for invalid fds, missing paths, and invalid flags.
The source-level description states or implies: Copyright (c) 2020 Viresh Kumar <viresh.kumar@linaro.org> Basic move_mount() failure tests.

## Important APIs, Types, and Functions
Key local functions: `run()`.
Primary syscall/API surface: `move_mount`, `fsopen`, `fsconfig`, `fsmount`.
LTP and helper APIs used include: `SAFE_CLOSE`, `SAFE_UMOUNT`, `TEST`, `fsconfig`, `fsmount`, `fsopen`, `move_mount`, `tst_device`, `tst_res`, `tst_strerrno`, `tst_test`.
Harness fields present in `struct tst_test`: `.all_filesystems`, `.format_device`, `.mntpoint`, `.needs_root`, `.setup`, `.skip_filesystems`, `.tcnt`, `.test`.

## Control Flow
The modern LTP harness enters through `.test` after optional `.setup`; it runs one case or iterates `.tcnt` table entries, records results with `tst_res`/`TST_EXP_*`, and then invokes `.cleanup` for mapped memory, descriptors, mounts, queues, or credentials.
The file contains table-driven state, with roughly 4 initializer blocks controlling argument combinations, expected errnos, flags, or variants.

## State and Persistence
Persistent or externally visible state includes mount namespace, mounted filesystems, and mount flags; temporary files, file descriptors, or LTP temp directories. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `move_mount` syscall test directory. new mount API wrappers fsopen/fsconfig/fsmount/open_tree/move_mount, root privileges, formatted devices, tmpfs, and kernel-version gates.

## Risks
Risks: requires privilege and may produce misleading failures if user switching or capability assumptions differ; mount and filesystem coverage can vary by kernel, filesystem support, and cleanup ordering.

## Test Signals
explicit TPASS/TST_EXP_PASS checks mark expected syscall behavior; negative paths validate exact errno or unexpected-success handling.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/move_mount/move_mount02.c -->
