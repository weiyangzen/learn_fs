<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/tee/tee02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/tee/tee02.c

Purpose: Verify that, tee(2) returns -1 and sets errno to: 1. EINVAL if fd_in does not refer to a pipe. 2. EINVAL if fd_out does not refer to a pipe. 3. EINVAL if fd_in and fd_out refer to the same pipe.

Important APIs/types/functions: includes `sys/types.h`, `sys/stat.h`, `fcntl.h`, `unistd.h`, `tst_test.h`, `lapi/tee.h`; exercises `tee`; defines `setup`, `tee_verify`, `cleanup`; uses constants `EINVAL`, `O_CREAT`, `O_RDWR`.

Control flow centers on `setup`, `tee_verify`, `cleanup`. The `struct tst_test` registration wires `.setup`, `.cleanup`, `.test`, `.tcnt`, `.needs_tmpdir` into the runner. Error-path expectations include `EINVAL`.

State and persistence behavior: Runtime state is pipe buffer contents and duplicated pipe references; `tee()` copies data between pipes without consuming the input buffer.

Dependencies and integration points: Depends on pipe setup, splice/tee syscall wrappers, page-sized buffers, and non-consuming pipe duplication semantics. Direct include dependencies include `sys/types.h`, `sys/stat.h`, `fcntl.h`, `unistd.h`, `tst_test.h`, `lapi/tee.h`.

Risks and test signals: Pipe buffer accounting and non-consuming semantics are subtle; false failures can come from partial writes or incorrect read ordering. Test signals: reports through `TFAIL`, `TPASS`, `TST_ERR`, `TST_RET`, `TTERRNO`; checks errno values `EINVAL`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/tee/tee02.c -->
