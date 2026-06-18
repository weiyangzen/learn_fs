<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/symlink/symlink03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/symlink/symlink03.c

Purpose: (at your option) any later version. This program is distributed in the hope that it will be useful, Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA Test Name : symlink03 Test Description : Verify that, 1) symlink(2) returns -1 and sets errno to EACCES if search/write permission is denied in the directory where the symbolic link is being created. 2) symlink(2) returns -1 and sets errno to EEXIST if the specified symbolic link already exists. 3) symlink(2) returns -1 and sets errno to EFAULT if the specified file or symbolic link points to invalid address. 4) symlink(2) returns -1 and sets errno to ENAMETOOLONG if the pathname component of symbolic link is too long (ie, > PATH_MAX). 5) symlink(2) returns -1 and sets errno to ENOTDIR if the directory component in pathname of symbolic link is not a directory. 6) s

Important APIs/types/functions: includes `stdio.h`, `sys/types.h`, `fcntl.h`, `sys/mman.h`, `errno.h`, `string.h`, `signal.h`, `sys/stat.h`; exercises `symlink`, `syscall`, `times`, `fork`, `write`, `open`, `close`, `chmod`; defines `no_setup`, `setup1`, `setup2`, `setup3`, `longpath_setup`, `setup`, `cleanup`, `main`; uses constants `EACCES`, `EEXIST`, `EFAULT`, `ENAMETOOLONG`, `ENOENT`, `ENOTDIR`, `O_CREAT`, `O_RDWR`, `SIGUSR1`.

Control flow centers on `no_setup`, `setup1`, `setup2`, `setup3`, `longpath_setup`, `setup`, `cleanup`, `main`. This is an older harness test using `tst_parse_opts()`, `TEST_LOOPING()`, and explicit cleanup. Error-path expectations include `EACCES`, `EEXIST`, `EFAULT`, `ENAMETOOLONG`, `ENOENT`, `ENOTDIR`.

State and persistence behavior: Runtime state is pathname namespace fixtures: regular files, nonexistent targets, symlinks, long paths, permissions, and lstat-visible link metadata.

Dependencies and integration points: Depends on LTP filesystem fixtures, safe path helpers, legacy bad-address helpers in old tests, and lstat/readlink-visible symlink semantics. Direct include dependencies include `stdio.h`, `sys/types.h`, `fcntl.h`, `sys/mman.h`, `errno.h`, `string.h`.

Risks and test signals: Path length, permission, bad-address, and legacy harness behavior can vary; the durable signal is correct errno or lstat-visible link state. Test signals: reports through `TBROK`, `TERRNO`, `TFAIL`, `TINFO`, `TPASS`, `TST_TOTAL`; checks errno values `EACCES`, `EEXIST`, `EFAULT`, `ENAMETOOLONG`, `ENOENT`, `ENOTDIR`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/symlink/symlink03.c -->
