<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl32.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl32.c

Purpose: Checks write leases against duplicate opens and verifies expected lease break behavior for read/write access combinations. Source notes: Author: Guangwen Feng <fenggw-fnst@cn.fujitsu.com> This program is free software; you can redistribute it and/or modify it under the terms of version 2 of the GNU General Public License as published by the Free Software Foundation. This program is distributed in the hope that it would be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. You should have received a copy of the GNU General Public License alone with this program. DESCRIPTION Basic test for fcntl(2) using F_SETLEASE & F_WRLCK argument. "A write lease may be placed on a file only if there are no other open file descriptors for the file." The file was read in full for this report (137 lines, 2939 bytes).

Important APIs/types/functions: calls/wrappers: fcntl(), close(), SAFE_TOUCH, SAFE_OPEN, SAFE_CLOSE; types/structs: struct test_case_t; functions: main, setup, verify_fcntl, cleanup; local macros/constants: FILE_MODE.

Control flow: setup path: setup; exercise path: main, verify_fcntl; cleanup path: cleanup; notable execution mechanics: iterates a case table.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents, advisory locks or file leases. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `errno.h`, `test.h`, `tso_safe_macros.h`; integrates with the LTP fcntl syscall suite; uses the LTP C harness and result macros.

Risks: filesystem-specific semantics can change expected results.

Test signals: explicit pass reporting; explicit failure reporting; errno checks: EBUSY, EAGAIN; key constants: F_SETLEASE, F_WRLCK, O_RDONLY, O_WRONLY, O_RDWR.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fcntl/fcntl32.c -->
