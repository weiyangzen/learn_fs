# sources/test-tools/liburing/test/sq-space_left.c

Purpose: tests liburing SQ space accounting before fill, after each `get_sqe`, and after partial submission failure caused by an invalid opcode.

Important APIs/types/functions: `io_uring_sq_space_left`, `io_uring_sq_ready`, `io_uring_get_sqe`, `io_uring_prep_nop`, `io_uring_submit`, and invalid opcode `0xfe`.

Control flow: `test_left()` fills an 8-entry ring one SQE at a time and checks remaining space after every acquisition. `test_sync()` queues 8 NOPs, one invalid opcode, then 8 more NOPs; submit should process 8 successes plus the bad request, leave the trailing 8 ready, then a second submit should clear them.

State/persistence behavior: only local SQ state is used; no requests need CQE validation.

Dependencies/integration: covers liburing userspace SQ accounting and kernel submission-stop behavior on invalid opcodes.

Risks/test signals: catches stale SQ-ready counts, space-left miscounting, or failure to preserve trailing SQEs after a synchronous submission error.
