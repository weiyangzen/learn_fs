# sources/test-tools/liburing/test/sqpoll-disable-exit.c

Purpose: syzkaller-derived regression for SQPOLL/ring setup teardown involving disabled/large ring parameters and process exit under repeated forks.

Important APIs/types/functions: raw `__sys_io_uring_setup`, manual `mmap` of SQ/CQ rings and SQEs, fixed virtual addresses, process groups, `PR_SET_PDEATHSIG`, `oom_score_adj`, fork/kill/wait loops, and sanitizer skip guard.

Control flow: outside sanitizer builds, `main()` maps syzkaller-style memory regions and runs 100 iterations. Each child sets death-signal/process-group state and calls `execute_one()`, which writes crafted `io_uring_params` fields in mapped memory and invokes setup for a large entry count. Parent kills children that exceed five seconds and includes fuse abort cleanup logic.

State/persistence behavior: no durable files; it writes `/proc/self/oom_score_adj` and manipulates process/killing state. The core state is kernel ring setup/exit behavior under abnormal child teardown.

Dependencies/integration: includes raw syscall wrapper and syzkaller reproduction code; sanitizer builds return skip to avoid incompatible instrumentation.

Risks/test signals: designed to expose hangs, teardown leaks, or crashes. It has little semantic assertion beyond bounded child exit.
