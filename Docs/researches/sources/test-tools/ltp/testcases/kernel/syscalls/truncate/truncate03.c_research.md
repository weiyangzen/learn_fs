<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/truncate/truncate03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/truncate/truncate03.c

Purpose: 07/2001 John George Verify that: - truncate(2) returns -1 and sets errno to EACCES if search/write permission denied for the process on the component of the path prefix or named file. - truncate(2) returns -1 and sets errno to ENOTDIR if the component of the path prefix is not a directory. - truncate(2) returns -1 and sets errno to EFAULT if pathname points outside user's accessible address space. - truncate(2) returns -1 and sets errno to ENAMETOOLONG if the component of a pathname exceeded 255 characters or entire pathname exceeds 1023 characters. - truncate(2) returns -1 and sets errno to ENOENT if the named file does not exist. - truncate(2) returns -1 and sets errno to EISDIR if the named file is a directory. - truncate(2) returns -1 and sets errno to EFBIG if the argument length is larger than the maximum file size. - truncate(2) re

Important APIs/types/functions: includes `stdio.h`, `sys/types.h`, `sys/stat.h`, `fcntl.h`, `sys/mman.h`, `errno.h`, `string.h`, `signal.h`; exercises `truncate`, `write`; defines `setup`, `verify_truncate`; uses constants `EACCES`, `EFAULT`, `EFBIG`, `EISDIR`, `ELOOP`, `ENAMETOOLONG`, `ENOENT`, `ENOTDIR`, `SIGXFSZ`, `SIG_BLOCK`.

Control flow centers on `setup`, `verify_truncate`. The `struct tst_test` registration wires `.needs_root`, `.needs_tmpdir`, `.setup`, `.tcnt`, `.test` into the runner. Error-path expectations include `EACCES`, `EFAULT`, `EFBIG`, `EISDIR`, `ELOOP`, `ENAMETOOLONG`, `ENOENT`, `ENOTDIR`.

State and persistence behavior: Runtime state is regular file content, length, descriptor offsets, permissions, symlink loops, resource limits, and filesystem error paths.

Dependencies and integration points: Depends on temporary filesystem fixtures, `truncate(2)`, resource limits, bad-address helpers, credential switching, and filesystem-specific error behavior. Direct include dependencies include `stdio.h`, `sys/types.h`, `sys/stat.h`, `fcntl.h`, `sys/mman.h`, `errno.h`.

Risks and test signals: Filesystem permissions, RLIMIT_FSIZE, symlink-loop limits, and bad-address checks vary; setup must isolate each errno path. Test signals: reports through `TST_EXP_FAIL`; checks errno values `EACCES`, `EFAULT`, `EFBIG`, `EISDIR`, `ELOOP`, `ENAMETOOLONG`, `ENOENT`, `ENOTDIR`; depends on privilege or credential transitions.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/truncate/truncate03.c -->
