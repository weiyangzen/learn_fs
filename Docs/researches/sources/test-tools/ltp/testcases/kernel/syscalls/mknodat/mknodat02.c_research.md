# sources/test-tools/ltp/testcases/kernel/syscalls/mknodat/mknodat02.c

Purpose: Description: Verify that, 1) mknod(2) returns -1 and sets errno to EROFS if pathname refers to a file on a read-only file system. 2) mknod(2) returns -1 and sets errno to ELOOP if Too many symbolic links were encountered in resolving pathname.

Important APIs/types/functions: open, close, mknod, mknodat, mkdir, symlink, unlinkat, mount, TST_TOTAL, tst_parse_opts, tst_count, tst_exit, tst_require_root, tst_sig, tst_tmpdir, tst_dev_fs_type, tst_acquire_device, tst_brkm, tst_mkfs, SAFE_MKDIR, SAFE_MOUNT, SAFE_OPEN, SAFE_SYMLINK, tst_resm, tst_syscall, tst_umount, tst_release_device, tst_rmdir; local functions detected: main, setup, mknodat_verify, cleanup; key constants/macros: DIR_MODE, MNT_POINT, FIFOMODE, FREGMODE, SOCKMODE, ELOPFILE

Control flow: Legacy LTP flow: `main()` parses options, calls setup, loops TEST_LOOPING over testcase entries, invokes verification helpers, then cleanup/tst_exit. Local functions: main, setup, mknodat_verify, cleanup.

State and persistence behavior: temporary files/directories created under the LTP tmpdir; root privileges for namespace, xattr, device, resource-limit, or permission checks; mounted scratch filesystem/device state. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers; spare block device or loop-backed LTP device. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: exact errno expectations can vary when prerequisites are missing or a filesystem rejects setup earlier; mount/device availability and filesystem semantics affect read-only and node-creation cases.

Test signals: explicit TPASS/TFAIL result messages; TCONF skips for unsupported kernel/library/filesystem features; TBROK on setup or invariant failure. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.

Additional source notes: mount a read-only file system for EROFS test NOTE: the ELOOP test is written based on that the consecutive symlinks limits in kernel is hardwired to 40.
