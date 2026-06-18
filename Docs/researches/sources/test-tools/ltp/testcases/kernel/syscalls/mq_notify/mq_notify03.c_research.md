<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mq_notify/mq_notify03.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mq_notify/mq_notify03.c

## Purpose
This file glibc CVE-2021-38604 regression for SIGEV_THREAD notifier unregister/re-register NULL dereference behavior.
The source-level description states or implies: Test for NULL pointer dereference in mq_notify(CVE-2021-38604) References links: - https://sourceware.org/bugzilla/show_bug.cgi?id=28213

## Important APIs, Types, and Functions
Key local functions: `try_null_dereference_cb()`, `try_null_dereference()`, `do_test()`.
Primary syscall/API surface: `mq_notify`, `mq_unlink`.
LTP and helper APIs used include: `SAFE_MQ_OPEN`, `TST_EXP_PASS`, `TST_EXP_VAL`, `mq_attr`, `mq_maxmsg`, `mq_msgsize`, `mq_notify`, `mq_receive`, `mq_send`, `mq_unlink`, `tst_safe_posix_ipc`, `tst_tag`, `tst_test`.
Harness fields present in `struct tst_test`: `.needs_root`, `.tags`, `.test_all`.

## Control Flow
The modern LTP harness enters through `.test_all` after optional `.setup`; it runs one case or iterates `.tcnt` table entries, records results with `tst_res`/`TST_EXP_*`, and then invokes `.cleanup` for mapped memory, descriptors, mounts, queues, or credentials.
The file contains table-driven state, with roughly 1 initializer blocks controlling argument combinations, expected errnos, flags, or variants.

## State and Persistence
Persistent or externally visible state includes POSIX message queue objects and notification registration; child/thread synchronization and signal-observed outcomes; temporary files, file descriptors, or LTP temp directories. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `mq_notify` syscall test directory. POSIX message queues, tst_safe_posix_ipc, common mq helpers, signal/thread notification, pthread and realtime linkage.
Regression tags link the scenario to upstream commits or CVEs, which are useful signals when triaging failures.

## Risks
Risks: requires privilege and may produce misleading failures if user switching or capability assumptions differ; signal or child-process expectations can be timing-sensitive.

## Test Signals
explicit TPASS/TST_EXP_PASS checks mark expected syscall behavior.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mq_notify/mq_notify03.c -->
