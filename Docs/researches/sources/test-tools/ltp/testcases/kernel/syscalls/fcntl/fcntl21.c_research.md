<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl21.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl21.c

Purpose: Legacy record-lock stress test that forks a child and parent to exercise POSIX byte-range locking, `F_SETLK`, `F_SETLKW`, and `F_GETLK` over a temporary file containing known alphabet data. Source notes: This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details. You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA NAME fcntl21.c DESCRIPTION Check locking of regions of a file ALGORITHM Test changing lock sections around a read lock USAGE fcntl21 HISTORY 07/2001 Ported by Wayne Boyer... The file was read in full for this report (849 lines, 18439 bytes).

Important APIs/types/functions: calls/wrappers: fcntl(), wait(), close(), pipe(), read(), write(), sigaction(); types/structs: struct flock, struct sigaction; functions: setup, cleanup, do_child, do_lock, do_test, compare_lock, unlock_file, parent_put, parent_get, child_put, child_get, stop_child, catch_child, main; local macros/constants: STRINGSIZE, STRING, STOP.

Control flow: setup path: setup; exercise path: do_child, do_lock, do_test, parent_put, parent_get, child_put, child_get, stop_child, catch_child, main; cleanup path: cleanup; notable execution mechanics: forks child processes for concurrency or privilege separation.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, child processes and wait status, advisory locks or file leases. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `fcntl.h`, `errno.h`, `signal.h`, `sys/types.h`, `sys/stat.h`, `sys/wait.h`, `inttypes.h`, `test.h`; integrates with the LTP fcntl syscall suite; uses the LTP C harness and result macros.

Risks: scheduler timing and signal ordering can make failures hard to diagnose.

Test signals: explicit failure reporting; key constants: PATH_MAX, SIGCHLD, F_GETLK, F_SETLK, F_UNLCK, F_WRLCK, F_RDLCK.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl21.c -->
