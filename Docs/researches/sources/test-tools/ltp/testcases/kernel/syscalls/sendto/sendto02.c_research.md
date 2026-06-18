<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sendto/sendto02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/sendto/sendto02.c

Purpose: When SCTP protocol created wih socket(2) and buffer is invalid, sendto(2) should fail and set errno to EFAULT, but it sets errno to ENOMEM. This is a regression test fixed by kernel 3.7 6e51fe757259 (sctp: fix -ENOMEM result with invalid user space pointer in sendto() syscall) In this shard it contributes focused coverage for sendto socket error, SCTP, packet socket, and overflow regression coverage.

Important APIs/types/functions: uses new LTP API (`tst_test`, `TST_EXP_*`, `SAFE_*` helpers). Key local functions: `setup`, `cleanup`, `verify_sendto`. Key structs/tables: none explicit. Important syscall/helper surface includes: `SAFE_CLOSE`, `TEST`, `TST_ERR`, `TST_RET`, `sendto`, `sets`, `setup`, `tst_brk`, `tst_res`, `tst_tag`, `tst_test`.

Control flow: The `struct tst_test` registration drives setup, cleanup, variant selection, and test callbacks through the new LTP runner. important local functions are `setup`, `cleanup`, `verify_sendto`.

State and persistence behavior: exercises socket endpoints or file-transfer descriptors. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on standard libc/Linux syscall headers plus LTP assertion and safe-wrapper helpers. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: regression tags tie behavior to specific kernel fixes.

Test signals: pass/fail is reported through TST_RET, tst_res. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/sendto/sendto02.c -->
