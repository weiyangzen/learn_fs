<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl22.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl22.c

Purpose: Checks `F_SETLK` contention: a parent holds a write lock, the child attempts a conflicting nonblocking lock, and the expected result is `EAGAIN`. Source notes: This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details. You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA Test Name: fcntl22 Test Description: Verify that, fcntl() fails with -1 and sets errno to EAGAIN when Operation is prohibited by locks held by other processes. Expected Re... The file was read in full for this report (127 lines, 2772 bytes).

Important APIs/types/functions: calls/wrappers: fcntl(), close(); types/structs: struct flock; functions: main, setup, cleanup.

Control flow: setup path: setup; exercise path: main; cleanup path: cleanup; notable execution mechanics: forks child processes for concurrency or privilege separation.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, child processes and wait status, advisory locks or file leases. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `fcntl.h`, `errno.h`, `signal.h`, `stdlib.h`, `sys/types.h`, `sys/wait.h`, `test.h`; integrates with the LTP fcntl syscall suite; uses the LTP C harness and result macros.

Risks: scheduler timing and signal ordering can make failures hard to diagnose.

Test signals: explicit pass reporting; explicit failure reporting; errno checks: EAGAIN; key constants: F_SETLK, F_WRLCK.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl22.c -->
