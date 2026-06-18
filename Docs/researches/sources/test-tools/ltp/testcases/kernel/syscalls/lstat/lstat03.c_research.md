# sources/test-tools/ltp/testcases/kernel/syscalls/lstat/lstat03.c

Purpose: This test verifies that lstat() provides correct information according with device, access time, block size, ownership, etc. The implementation provides a set of tests which are specific for each one of the `struct stat` used to read file and symlink information.

Important APIs/types/functions: open, close, lstat, stat, symlink, mount, umount, tst_test, SAFE_LSTAT, TST_EXP_EXPR, SAFE_STAT, SAFE_MKFS, tst_device, SAFE_MOUNT, SAFE_TOUCH, SAFE_LINK, SAFE_CHOWN, SAFE_OPEN, tst_fill_fd, TST_KB, SAFE_CLOSE, SAFE_SYMLINK, tst_is_mounted, SAFE_UMOUNT, tst_buffers; local functions detected: run, setup, cleanup; key constants/macros: FILENAME, MNTPOINT, SYMBNAME

Control flow: setup prepares fixtures; test_all runs one whole-file scenario; cleanup releases descriptors, mappings, mounts, ACLs, or memory. Local helper functions: run, setup, cleanup.

State and persistence behavior: temporary files/directories created under the LTP tmpdir; root privileges for namespace, xattr, device, resource-limit, or permission checks; mounted scratch filesystem/device state. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers; spare block device or loop-backed LTP device. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: mount/device availability and filesystem semantics affect read-only and node-creation cases.

Test signals: TST_EXP_* value comparisons. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.

Additional source notes: change st_blksize / st_dev change st_uid and st_gid
