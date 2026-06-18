<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sendmsg/sendmsg02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sendmsg/sendmsg02.c

Purpose: Copyright (C) 2013 Linux Test Project This program is free software; you can redistribute it and/or modify it under the terms of version 2 of the GNU General Public License as published by the Free Software Foundation. This program is distributed in the hope that it would be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. Further, this software is distributed without any warranty that it is free of the rightful claim of any third person regarding infringement or the like. Any license provided herein, whether implied or otherwise, applies only to this software file. In this shard it contributes focused coverage for sendmsg socket error and security regression coverage.

Important APIs/types/functions: uses legacy LTP API (`test.h`, `TEST`, `tst_resm`, `tst_brkm`). Key local functions: `client`, `server`, `reproduce`, `help`, `main`, `setup`, `cleanup`. Key structs/tables: none explicit. Important syscall/helper surface includes: `GETVAL`, `SAFE_MALLOC`, `SAFE_STRTOL`, `SETVAL`, `TEST_LOOPING`, `sendmsg`, `setting`, `setup`, `tst_brkm`, `tst_exit`, `tst_parse_opts`, `tst_require_root`, `tst_resm`, `tst_rmdir`, `tst_tmpdir`.

Control flow: A legacy `main()` parses LTP options, runs setup, loops with `TEST_LOOPING`, executes cases, then calls cleanup and `tst_exit()`. important local functions are `client`, `server`, `reproduce`, `help`, `main`, `setup`, `cleanup`.

State and persistence behavior: exercises forked child state; temporary files or descriptors; socket endpoints or file-transfer descriptors. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on root privileges. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: requires privilege and may be skipped or fail under restricted runners; child cleanup and wait ordering matter; timing-sensitive behavior can be flaky on overloaded systems.

Test signals: pass/fail is reported through tst_resm, tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sendmsg/sendmsg02.c -->
