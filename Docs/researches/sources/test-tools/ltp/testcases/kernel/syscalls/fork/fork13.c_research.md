<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fork/fork13.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/fork/fork13.c

Purpose: Validates fork under resource limit or memory pressure setup and expected failure/success reporting. Source notes: \ A race in pid generation that causes pids to be reused immediately From the mainline commit 5fdee8c4a5e1 ("pids: fix a race in pid generation that causes pids to be reused immediately") A program that repeatedly forks and waits is susceptible to having the same pid repeated, especially when it competes with another instance of the same program. This is really bad for bash implementation. Furthermore, many shell scripts assume that pid numbers will not be used for some length of time. [Race Description] :: A B // pid == offset == n // pid == offset == n + 1 test_and_set_bit(offset, map->page) test_and_set_bit(offset, map->page); pid_ns->last_pid = pid; pid_ns->last_pid = pid; // pid == n + 1 is freed (wait()) // Next fork()... last = pid_ns->last_pid; // == n pid = last + 1; The distance mod PIDMAX between two pids, where the first pi... The file was read in full for this report (121 lines, 3044 bytes).

Important APIs/types/functions: calls/wrappers: fork(), wait(), SAFE_FORK, SAFE_WAITPID; types/structs: struct tst_test, struct tst_path_val, struct tst_tag; functions: pid_distance, check; local macros/constants: PID_MAX, PID_MAX_STR, RETURN, MAX_ITERATIONS.

Control flow: the file provides declarations/helpers consumed by sibling tests; notable execution mechanics: forks child processes for concurrency or privilege separation.

State and persistence behavior: The test manipulates child processes and wait status, UID/capability-sensitive kernel state. Cleanup and SAFE_* wrappers are responsible for closing descriptors, unmapping memory, restoring tunables, removing temporary files, and reaping children where applicable.

Dependencies and integration points: includes `sys/types.h`, `sys/stat.h`, `sys/wait.h`, `fcntl.h`, `errno.h`, `unistd.h`, `stdio.h`, `stdlib.h`, `tst_test.h`; integrates with the LTP fork syscall suite; uses the LTP C harness and result macros.

Risks: requires root/capability-sensitive behavior; scheduler timing and signal ordering can make failures hard to diagnose.

Test signals: explicit pass reporting; explicit failure reporting; key constants: PATH_KERN_PID_MAX; harness metadata: .needs_root, .forks_child, .test_all, .tags.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/fork/fork13.c -->
