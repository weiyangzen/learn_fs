<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/futimesat/futimesat01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/futimesat/futimesat01.c

Purpose: published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version. but WITHOUT ANY WARRANTY; without even the implied warranty of along with this program. If not, see <http://www.gnu.org/licenses/>. DESCRIPTION This test case will verify basic function of futimesat added by kernel 2.6.16 or up. Author Yi Yang <yyangcdl@cn.ibm.com>

Important APIs/types/functions: includes `sys/types.h`, `sys/stat.h`, `sys/time.h`, `fcntl.h`, `stdlib.h`, `errno.h`, `string.h`, `signal.h`; touches `futimesat`, `gettimeofday`, `raw syscall path`; defines `setup`, `cleanup`, `myfutimesat`, `main`; uses LTP safe helpers such as `SAFE_ASPRINTF`, `SAFE_FILE_PRINTF`, `SAFE_MKDIR`, `SAFE_OPEN`.

Control flow centers on `setup`, `cleanup`, `myfutimesat`, `main`. This is a legacy LTP test with an explicit `main()` loop and setup/cleanup calls. Error-path assertions cover `EBADF`, `ENOTDIR`.

State and persistence behavior: Runtime state is filesystem metadata: fixture files/directories, file descriptors, and atime/mtime values changed through futimesat.

Dependencies and integration points: Depends on the LTP test framework, Linux syscall/lapi wrappers, safe fixture helpers, and libc/kernel headers selected by the source. Direct include dependencies include `sys/types.h`, `sys/stat.h`, `sys/time.h`, `fcntl.h`, `stdlib.h`, `errno.h`.

Risks and test signals: The main risk is environment sensitivity: kernel configuration, capabilities, filesystem support, libc/syscall variant differences, scheduler timing, or architecture ABI can turn intended assertions into skips or false failures. Test signals are emitted through `TFAIL`, `TPASS`, `TST_TOTAL`. Expected errno values include `EBADF`, `ENOTDIR`.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/futimesat/futimesat01.c -->
