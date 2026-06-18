<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fstatat/fstatat01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fstatat/fstatat01.c

Purpose: Table-driven `fstatat()` coverage for dirfd-relative paths, symlinks, empty path, and expected errno cases. Source notes: This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version. This program is distributed in the hope that it would be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details. You should have received a copy of the GNU General Public License along with this program. If not, see <http://www.gnu.org/licenses/>. DESCRIPTION This test case will verify basic function of fstatat64/newfstatat added by kernel 2.6.16 or up. Author Yi Yang <yyangcdl@cn.ibm.com> The file was read in full for this report (152 lines, 3678 bytes).

Important APIs/types/functions: calls/wrappers: fstatat(), close(), SAFE_ASPRINTF, SAFE_MKDIR, SAFE_OPEN, SAFE_FILE_PRINTF; types/structs: struct stat64, struct stat; functions: fstatat, main, setup, cleanup; local macros/constants: TEST_CASES, AT_FDCWD.

Control flow: setup path: setup; exercise path: main; cleanup path: cleanup.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, kernel tunables that setup/cleanup must restore. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `sys/types.h`, `sys/stat.h`, `sys/time.h`, `fcntl.h`, `stdlib.h`, `errno.h`, `string.h`, `signal.h`, `config.h`, `test.h`, `tso_safe_macros.h`, `lapi/syscalls.h`; integrates with the LTP fstatat syscall suite; uses the LTP C harness and result macros; uses LTP Linux API compatibility headers.

Risks: expected errno/return-value assertions are sensitive to kernel and libc behavior.

Test signals: explicit pass reporting; explicit failure reporting; errno checks: ENOTDIR, EBADF, EINVAL; key constants: AT_FDCWD, __NR_fstatat64, __NR_newfstatat, __NR_fstatat, O_DIRECTORY, O_CREAT, O_RDWR.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fstatat/fstatat01.c -->
