<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fork/fork05.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fork/fork05.c

Purpose: Checks fork behavior with signal handling or child exit status propagation. Source notes: Author: Ulrich Drepper / Nate Straz , Red Hat \ This test verifies that LDT is propagated correctly from parent process to the child process. On Friday, May 2, 2003 at 09:47:00AM MST, Ulrich Drepper wrote: Robert Williamson wrote: I'm getting a SIGSEGV with one of our tests, fork05.c, that apparently you wrote (attached below). The test passes on my 2.5.68 machine running SuSE 8.0 (glibc 2.2.5 and Linuxthreads), however it segmentation faults on RedHat 9 running 2.5.68. The test seems to "break" when it attempts to run the assembly code....could you take a look at it? There is no need to look at it, I know it cannot work anymore on recent systems. Either change all uses of %gs to %fs or skip the entire patch if %gs has a nonzero value. On Sat, Aug 12, 2000 at 12:47:31PM -0700, Ulrich Drepper wrote: Ever since the %gs handling was fixed... The file was read in full for this report (117 lines, 3205 bytes).

Important APIs/types/functions: calls/wrappers: SAFE_MODIFY_LDT, SAFE_FORK, TST_EXP_EQ_LI, SAFE_WAITPID, TST_TEST_TCONF; types/structs: struct user_desc, struct tst_test; functions: run.

Control flow: exercise path: run; notable execution mechanics: forks child processes for concurrency or privilege separation.

State and persistence behavior: The test manipulates child processes and wait status. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `tst_test.h`, `lapi/ldt.h`; integrates with the LTP fork syscall suite; uses the LTP C harness and result macros; uses LTP Linux API compatibility headers.

Risks: scheduler timing and signal ordering can make failures hard to diagnose.

Test signals: explicit pass reporting; explicit failure reporting; key constants: SIGSEGV; harness metadata: .test_all, .forks_child.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fork/fork05.c -->
