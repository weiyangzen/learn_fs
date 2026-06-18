# sources/test-tools/ltp/testcases/kernel/syscalls/mkdir/mkdir03.c

Purpose: Check mkdir() with various error conditions that should produce EFAULT, ENAMETOOLONG, EEXIST, ENOENT, ENOTDIR, ELOOP and EROFS. Testing on various types of files (symlinks, directories, pipes, devices, etc).

Important APIs/types/functions: mkdir, symlink, tst_test, TST_EEXIST, tst_eexist, TST_PIPE, tst_pipe, TST_FOLDER, tst_folder, TST_SYMLINK, tst_symlink, TST_NULLDEV, TST_ENOENT, tst_enoent, TST_ENOTDIR_FILE, tst_enotdir, TST_ENOTDIR_DIR, TST_EROFS, tst_erofs, TST_RET, tst_res, TST_ERR, SAFE_SYMLINK, tst_tmpdir_path, SAFE_MKFIFO, SAFE_MKDIR, SAFE_TOUCH, tst_get_bad_addr; local functions detected: verify_mkdir, setup; key constants/macros: TST_EEXIST, TST_PIPE, TST_FOLDER, TST_SYMLINK, TST_NULLDEV, TST_ENOENT, TST_ENOTDIR_FILE, TST_ENOTDIR_DIR, MODE, MNT_POINT, DIR_MODE, TST_EROFS

Control flow: setup prepares fixtures; test iterates over the testcase table. Local helper functions: verify_mkdir, setup.

State and persistence behavior: temporary files/directories created under the LTP tmpdir; root privileges for namespace, xattr, device, resource-limit, or permission checks. Artifacts are temporary test files, mappings, process state, mounts, or kernel-visible metadata and are expected to be cleaned by LTP tmpdir/device cleanup or file-local cleanup callbacks; no repository-persistent runtime state is written.

Dependencies and integration points: LTP harness headers and safe-macro wrappers. The file integrates with the LTP syscall suite through either `struct tst_test` or the legacy `test.h`/`tst_resm` harness, so build and execution are controlled by the enclosing syscall directory Makefile.

Risks and edge cases: exact errno expectations can vary when prerequisites are missing or a filesystem rejects setup earlier; mount/device availability and filesystem semantics affect read-only and node-creation cases.

Test signals: explicit TPASS/TFAIL result messages. A healthy run reports expected TPASS/TCONF/TBROK outcomes through the LTP result macros; failures usually indicate syscall semantic drift, missing kernel configuration, or fixture setup problems.
