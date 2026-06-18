<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/statmount.c -->
# sources/test-tools/strace/tests/statmount.c

## Purpose
Covers strace decoder coverage for `statmount`. Source comments/macros state: Check decoding of statmount syscall. End of VALID_STATMOUNT_STR STATMOUNT_??? bytes %zu..%zu MS_??? MS_??? MOUNT_ATTR_??? STATMOUNT_??? Source read: 666 lines, 19991 bytes.

## Important APIs, Types, And Functions
includes/imports: "tests.h", "scno.h", <stdio.h>, <string.h>, <unistd.h>, <linux/mount.h>; defines/undefs: INJ_STR, VALID_STATMOUNT, VALID_STATMOUNT_STR, INVALID_STATMOUNT, INVALID_STATMOUNT_STR, ALL_STATMOUNT, ALL_STATMOUNT_STR, VALID_SB_MAGIC, VALID_SB_MAGIC_STR, INVALID_SB_MAGIC, INVALID_SB_MAGIC_STR, VALID_SB_FLAGS, VALID_SB_FLAGS_STR, INVALID_SB_FLAGS, INVALID_SB_FLAGS_STR, ALL_SB_FLAGS, ALL_SB_FLAGS_STR, VALID_MOUNT_ATTR, VALID_MOUNT_ATTR_STR, INVALID_MOUNT_ATTR, INVALID_MOUNT_ATTR_STR, ALL_MOUNT_ATTR, ALL_MOUNT_ATTR_STR, VALID_MNT_PROPAGATION, VALID_MNT_PROPAGATION_STR, INVALID_MNT_PROPAGATION, INVALID_MNT_PROPAGATION_STR, ALL_MNT_PROPAGATION; C functions: k_statmount, test_req, test_stm_bad, test_stm_all_ops, test_stm_str_ops, test_stm_array_ops, main; syscall numbers/wrappers: statmount, __NR_statmount; struct types: mnt_id_req, statmount, stm_ops_t.

## Control Flow
`main` prepares synthetic inputs, invokes the target syscall/libc wrapper, prints the expected trace line, and returns through `+++ exited with 0 +++` style expectations. loops enumerate flag, pointer, descriptor, pid, or xlat-mode combinations. primary syscall coverage: statmount, __NR_statmount.

## State And Persistence Behavior
uses tail-allocated memory to place valid data beside unmapped or short-read boundaries.

## Dependencies And Integration Points
Depends on `tests.h`, `scno.h`, Linux UAPI headers, configured syscall-number availability. Integrated through the strace tests build, generated `.gen.test` wrappers, or direct compilation as a regression fixture.

## Risks And Test Signals
Risks: kernel or architecture may lack the syscall and require ENOSYS/skip handling; kernel configuration, procfs visibility, or privileges can change availability. Test signals: stdout emits canonical expected trace lines; return-code rendering is checked with `sprintrc`.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/statmount.c -->
