<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/symlinkat/symlinkat01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/symlinkat/symlinkat01.c

Purpose: (at your option) any later version. This program is distributed in the hope that it will be useful, Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA symlinkat01.c DESCRIPTION This test case will verify basic function of symlinkat added by kernel 2.6.16 or up. Author Yi Yang <yyangcdl@cn.ibm.com> 08/25/2006 Created first by Yi Yang <yyangcdl@cn.ibm.com> relative paths abs path at dst relative paths to cwd

Important APIs/types/functions: includes `sys/types.h`, `sys/stat.h`, `sys/time.h`, `fcntl.h`, `stdlib.h`, `errno.h`, `string.h`, `signal.h`; exercises `symlinkat`, `time`, `unlink`, `write`, `close`, `raw syscall path`; defines `setup`, `cleanup`, `setup_every_copy`, `mysymlinkat_test`, `mysymlinkat`, `main`; uses constants `AT_FDCWD`, `EBADF`, `ENOENT`, `ENOTDIR`, `O_CREAT`, `O_DIRECTORY`, `O_EXCL`, `O_RDONLY`, `O_RDWR`.

Control flow centers on `setup`, `cleanup`, `setup_every_copy`, `mysymlinkat_test`, `mysymlinkat`, `main`. This is an older harness test using `tst_parse_opts()`, `TEST_LOOPING()`, and explicit cleanup. Named case hints include `../`. Error-path expectations include `EBADF`, `ENOENT`, `ENOTDIR`.

State and persistence behavior: Runtime state is directory file descriptors plus relative symlink creation and readback in a temporary directory tree.

Dependencies and integration points: Depends on raw `symlinkat` syscall wrappers, directory fd setup, legacy LTP looping harness, and temporary directory cleanup. Direct include dependencies include `sys/types.h`, `sys/stat.h`, `sys/time.h`, `fcntl.h`, `stdlib.h`, `errno.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, privileges, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals: reports through `TFAIL`, `TPASS`, `TST_TOTAL`; checks errno values `EBADF`, `ENOENT`, `ENOTDIR`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/symlinkat/symlinkat01.c -->
