<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setpgrp/setpgrp02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/setpgrp/setpgrp02.c

Purpose: Copyright (c) International Business Machines Corp., 2001 07/2001 Ported by Wayne Boyer Copyright (c) Linux Test Project, 2001-2016 Copyright (C) 2024 SUSE LLC Andrea Manzini <andrea.manzini@suse.com> In this shard it contributes focused coverage for legacy and modern process group creation smoke tests.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `verify_setpgrp`. Key structs/tables: none explicit. Important syscall/helper surface includes: `SAFE_FORK`, `TST_EXP_PASS`, `setpgrp`, `tst_res`, `tst_test`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `verify_setpgrp`.

State and persistence behavior: exercises forked child state. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on standard libc/Linux syscall headers plus LTP assertion and safe-wrapper helpers. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: child cleanup and wait ordering matter.

Test signals: pass/fail is reported through TST_EXP_PASS, tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setpgrp/setpgrp02.c -->
