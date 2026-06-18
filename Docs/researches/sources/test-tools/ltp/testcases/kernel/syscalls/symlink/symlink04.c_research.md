<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/symlink/symlink04.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/symlink/symlink04.c

Purpose: Check that a symbolic link may point to an existing file or to a nonexistent one.

Important APIs/types/functions: includes `stdlib.h`, `stdio.h`, `tst_test.h`; exercises `symlink`; defines `setup`, `verify_symlink`.

Control flow centers on `setup`, `verify_symlink`. The `struct tst_test` registration wires `.tcnt`, `.setup`, `.test`, `.needs_tmpdir` into the runner.

State and persistence behavior: Runtime state is pathname namespace fixtures: regular files, nonexistent targets, symlinks, long paths, permissions, and lstat-visible link metadata.

Dependencies and integration points: Depends on LTP filesystem fixtures, safe path helpers, legacy bad-address helpers in old tests, and lstat/readlink-visible symlink semantics. Direct include dependencies include `stdlib.h`, `stdio.h`, `tst_test.h`.

Risks and test signals: Path length, permission, bad-address, and legacy harness behavior can vary; the durable signal is correct errno or lstat-visible link state. Test signals: reports through `TFAIL`, `TST_EXP_PASS`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/symlink/symlink04.c -->
