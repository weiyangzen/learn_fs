<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setpgid/setpgid03_child.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/setpgid/setpgid03_child.c

Purpose: Exercises process group mutation, session/exec restrictions, and checkpointed parent-child races. In this shard it contributes focused coverage for process group mutation, session/exec restrictions, and checkpointed parent-child races.

Important APIs/types/functions: uses mixed direct syscall and LTP helper API. Key local functions: `main`. Key structs/tables: none explicit. Important syscall/helper surface includes: `TST_CHECKPOINT_WAKE_AND_WAIT`, `TST_NO_DEFAULT_MAIN`, `tst_reinit`, `tst_test`.

Control flow: A legacy `main()` parses LTP options, runs setup, loops with `TEST_LOOPING`, executes cases, then calls cleanup and `tst_exit()`. important local functions are `main`.

State and persistence behavior: exercises mostly process-local syscall state with no durable repository state. Setup typically prepares only the resources needed by that test case and cleanup releases temporary resources or restores process-visible state. Persistent repository state is not modified.

Dependencies and integration points: depends on standard libc/Linux syscall headers plus LTP assertion and safe-wrapper helpers. The file integrates with the LTP syscall testcase layout through its directory Makefile and with related helper headers when present.

Risks: main risk is false pass/fail if the surrounding harness changes syscall wrappers or expected errno semantics.

Test signals: pass/fail is reported through compile success and absence of unexpected syscall errors. Meaningful success usually requires both the expected syscall return/errno and any postcondition check such as readback of IDs, priorities, offsets, signal status, memory placement, fd-set contents, or received data.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/setpgid/setpgid03_child.c -->
