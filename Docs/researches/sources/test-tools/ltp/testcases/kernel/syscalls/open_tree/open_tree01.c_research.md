<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/open_tree/open_tree01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/open_tree/open_tree01.c

Purpose: Basic :manpage:`open_tree(2)` test.

Important APIs/types/functions: includes `tst_test.h`, `lapi/fsmount.h`; exercises `open_tree`, `move_mount`; defines `cleanup`, `setup`, `run`; uses flags/constants `AT_FDCWD`, `MOVE_MOUNT_F_EMPTY_PATH`, `OPEN_TREE_CLOEXEC`, `OPEN_TREE_CLONE`.

Control flow centers on `cleanup`, `setup`, `run`. The `struct tst_test` registration wires `.tcnt`, `.test`, `.setup`, `.cleanup`, `.needs_root`, `.mount_device`, `.mntpoint`, `.all_filesystems`, `.skip_filesystems` into the LTP runner. Named case hints include `fuse`, `Flag `.

State and persistence behavior: Runtime state is mount topology: the mounted fixture at `MNTPOINT`, cloned mount file descriptors returned by `open_tree()`, and the destination mountpoint used by `move_mount()`.

Dependencies and integration points: Depends on `lapi/fsmount.h`, the fsopen/open_tree/move_mount wrappers, root privileges, mounted test devices, and filesystem skip lists. Direct include dependencies include `tst_test.h`, `lapi/fsmount.h`.

Risks and test signals: Mount API tests are kernel-version and filesystem sensitive; cleanup must close mount fds and unmount cloned mounts or later cases inherit stale topology. Test signals: reports through `TFAIL`, `TPASS`, `TST_RET`, `TTERRNO`; runs against mounted filesystem fixtures.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/open_tree/open_tree01.c -->
