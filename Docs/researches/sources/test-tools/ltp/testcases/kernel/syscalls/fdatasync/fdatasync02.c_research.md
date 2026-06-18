<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fdatasync/fdatasync02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fdatasync/fdatasync02.c

Purpose: Validates `fdatasync()` errno handling for invalid descriptors, read-only descriptors, pipes, and special descriptor states. Source notes: This program is free software; you can redistribute it and/or modify it under the terms of version 2 of the GNU General Public License as published by the Free Software Foundation. This program is distributed in the hope that it would be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. You should have received a copy of the GNU General Public License along with this program; if not, write the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA. ******************************************************** TEST IDENTIFIER : fdatasync02 EXECUTED BY : Any user TEST TITLE : Checking error conditions for fdatasync(2) TEST CASE TOTAL : 2 AUTHOR : Madhu T L <madhu.tarikere@wipro.com> SIGNALS Uses SIGUSR1 to pause before test if option... The file was read in full for this report (197 lines, 4908 bytes).

Important APIs/types/functions: calls/wrappers: fdatasync(), open(), SAFE_CLOSE; types/structs: struct test_case_t; functions: main, setup1, setup2, cleanup2, setup, cleanup; local macros/constants: EXP_RET_VAL, SPL_FILE.

Control flow: setup path: setup1, setup2, setup; exercise path: main; cleanup path: cleanup2, cleanup.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, child processes and wait status. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `errno.h`, `pwd.h`, `sys/types.h`, `sys/stat.h`, `fcntl.h`, `unistd.h`, `test.h`, `tso_safe_macros.h`; integrates with the LTP fdatasync syscall suite; uses the LTP C harness and result macros.

Risks: scheduler timing and signal ordering can make failures hard to diagnose.

Test signals: explicit pass reporting; explicit failure reporting; errno checks: EXECUTED, EBADF, EINVAL, EXP_RET_VAL; key constants: SIGNALS, SIGUSR1, O_RDONLY; harness metadata: .setup, .cleanup.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fdatasync/fdatasync02.c -->
