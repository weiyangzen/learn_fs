<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setgroups/setgroups02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/setgroups/setgroups02.c

Purpose: Copyright (c) International Business Machines Corp., 2001 Copyright (c) Linux Test Project, 2003-2023 07/2001 Ported by Wayne Boyer In this shard it contributes focused coverage for supplementary group list setting, bounds, privilege, and bad-pointer validation.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `verify_setgroups`. Key structs/tables: none explicit. Important syscall/helper surface includes: `GETGROUPS`, `SETGROUPS`, `TST_EXP_EQ_LI`, `TST_EXP_PASS`, `TST_EXP_VAL`, `setgroups`, `tst_buffers`, `tst_test`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `verify_setgroups`.

State and persistence behavior: exercises process credentials. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on 16-bit UID/GID compatibility wrappers, root privileges. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: requires privilege and may be skipped or fail under restricted runners.

Test signals: pass/fail is reported through TST_EXP_PASS, TST_EXP_EQ, TST_EXP_VAL. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setgroups/setgroups02.c -->
