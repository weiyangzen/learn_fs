<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl23.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl23.c

Purpose: Exercises `F_SETLEASE` with `F_RDLCK`, confirms `F_GETLEASE` reports the read lease, then releases it with `F_UNLCK`. Source notes: This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details. You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA ******************************************************** TEST IDENTIFIER : fcntl23 EXECUTED BY : anyone TEST TITLE : Basic test for fcntl(2) using F_SETLEASE & F_RDLCK arg... The file was read in full for this report (212 lines, 5475 bytes).

Important APIs/types/functions: calls/wrappers: fcntl(), open(), close(); functions: main, setup, cleanup.

Control flow: setup path: setup; exercise path: main; cleanup path: cleanup.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, advisory locks or file leases. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `sys/types.h`, `sys/stat.h`, `fcntl.h`, `unistd.h`, `errno.h`, `string.h`, `signal.h`, `test.h`; integrates with the LTP fcntl syscall suite; uses the LTP C harness and result macros.

Risks: filesystem-specific semantics can change expected results.

Test signals: explicit pass reporting; explicit failure reporting; errno checks: EXECUTED, ENVIRONMENTAL; key constants: F_SETLEASE, F_RDLCK, SIGNALS, SIGUSR1, F_GETLEASE, F_UNLCK, O_RDONLY, O_CREAT.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl23.c -->
