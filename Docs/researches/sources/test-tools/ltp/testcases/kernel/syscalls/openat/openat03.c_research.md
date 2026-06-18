<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/openat/openat03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/openat/openat03.c

Purpose: the License, or (at your option) any later version.

Important APIs/types/functions: includes `sys/types.h`, `sys/stat.h`, `unistd.h`, `errno.h`, `test.h`, `tso_safe_macros.h`, `lapi/fcntl.h`, `openat.h`; exercises `openat`, `read`, `fcntl`; defines `cleanup`, `setup`, `openat_tmp`, `write_file`, `test01`, `read_file`, `test02`, `link_tmp_file`, `test03`, `main`; uses flags/constants `AT_FDCWD`, `AT_SYMLINK_FOLLOW`, `O_RDWR`, `O_TMPFILE`.

Control flow centers on `cleanup`, `setup`, `openat_tmp`, `write_file`, `test01`, `read_file`, `test02`, `link_tmp_file`, `test03`, `main`. Error-path expectations include `EISDIR`, `ENOTSUP`.

State and persistence behavior: Runtime state is filesystem fixtures, directory file descriptors, process cwd handling, file status flags, symlinks, atime/mtime metadata, anonymous temporary files, and child exec inheritance of file descriptors.

Dependencies and integration points: Depends on the LTP safe-file helpers, `openat()` or raw syscall fallback, mount/testcase make rules, helper child binaries, and filesystem support for the specific open flags. Direct include dependencies include `sys/types.h`, `sys/stat.h`, `unistd.h`, `errno.h`, `test.h`, `tso_safe_macros.h`.

Risks and test signals: Open-flag coverage is filesystem and mount-option sensitive, especially `O_TMPFILE`, `O_NOATIME`, `O_DIRECT`, and large-file offsets. Test signals: reports through `TBROK`, `TCONF`, `TERRNO`, `TFAIL`, `TINFO`, `TPASS`, `TST_TOTAL`; checks errno values `EISDIR`, `ENOTSUP`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/openat/openat03.c -->
