<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sync_file_range/sync_file_range01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sync_file_range/sync_file_range01.c

Purpose: Basic error conditions test for sync_file_range() system call, tests for: - EBADFD Wrong filedescriptor - ESPIPE Unsupported file descriptor - EINVAL Wrong offset - EINVAL Wrong nbytes - EINVAL Wrong flags

Important APIs/types/functions: includes `sys/types.h`, `sys/stat.h`, `sys/utsname.h`, `endian.h`, `fcntl.h`, `stdio.h`, `stdlib.h`, `tst_test.h`; exercises `sync_file_range`, `raw syscall path`; defines `cleanup`, `setup`, `run_test`; uses constants `EBADF`, `EINVAL`, `ESPIPE`, `O_CREAT`, `O_RDWR`.

Control flow centers on `cleanup`, `setup`, `run_test`. The `struct tst_test` registration wires `.setup`, `.tcnt`, `.test`, `.cleanup`, `.needs_tmpdir` into the runner. Error-path expectations include `EBADF`, `EINVAL`, `ESPIPE`.

State and persistence behavior: Runtime state is dirty file ranges, file descriptors, offsets, flags, and block-device write counters before and after `sync_file_range()`.

Dependencies and integration points: Depends on `check_sync_file_range.h`, raw syscall wrappers, mounted test devices for writeback observation, and ordinary temp files for error paths. Direct include dependencies include `sys/types.h`, `sys/stat.h`, `sys/utsname.h`, `endian.h`, `fcntl.h`, `stdio.h`.

Risks and test signals: Range writeback behavior varies by filesystem and kernel; invalid-argument tests must distinguish unsupported syscall from real failure. Test signals: reports through `TCONF`, `TST_EXP_FAIL`; checks errno values `EBADF`, `EINVAL`, `ESPIPE`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sync_file_range/sync_file_range01.c -->
