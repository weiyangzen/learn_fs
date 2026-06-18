<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fmtmsg/fmtmsg01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fmtmsg/fmtmsg01.c

Purpose: Table-driven libc `fmtmsg()` validation over classification, severity, label/action/tag, environment variables, and return code combinations. Source notes: This program is free software; you can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation; either version 2 of the License, or (at your option) any later version. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details. You should have received a copy of the GNU General Public License along with this program; if not, write to the Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA 01/02/2003 Port to LTP avenkat@us.ibm.com 06/30/2001 Port to Linux nsharoff@us.ibm.com fmtmsg(3C) and addseverity(3C) ALGORITHM Check basic functionality using various mes... The file was read in full for this report (252 lines, 6086 bytes).

Important APIs/types/functions: calls/wrappers: fmtmsg(), close(); functions: clearbuf, main, anyfail, setup, blenter, blexit; local macros/constants: FAILED, PASSED.

Control flow: setup path: setup; exercise path: main; cleanup path: blexit.

State and persistence behavior: The test manipulates temporary files/descriptors and file contents. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `sys/types.h`, `sys/stat.h`, `fcntl.h`, `ctype.h`, `stdio.h`, `fmtmsg.h`, `string.h`, `stdlib.h`, `unistd.h`, `errno.h`, `test.h`; integrates with the LTP fmtmsg syscall suite; uses the LTP C harness and result macros.

Risks: expected errno/return-value assertions are sensitive to kernel and libc behavior.

Test signals: explicit pass reporting; explicit failure reporting; key constants: MM_PRINT, MM_SOFT, MM_INFO, MM_NOTOK, MM_OK, MM_HARD, MM_OPSYS, MM_CONSOLE.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fmtmsg/fmtmsg01.c -->
