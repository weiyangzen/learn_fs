<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mq_notify/mq_notify02.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mq_notify/mq_notify02.c

## Purpose
This file small mq_notify invalid sigevent argument test expecting EINVAL.
The source-level description states or implies: This test verifies that mq_notify() fails with EINVAL when invalid input arguments are given.

## Important APIs, Types, and Functions
Key local functions: `run()`.
Primary syscall/API surface: `mq_notify`.
LTP and helper APIs used include: `TST_EXP_FAIL`, `mq_notify`, `tst_test`.
Harness fields present in `struct tst_test`: `.tcnt`, `.test`.

## Control Flow
The modern LTP harness enters through `.test` after optional `.setup`; it runs one case or iterates `.tcnt` table entries, records results with `tst_res`/`TST_EXP_*`, and then invokes `.cleanup` for mapped memory, descriptors, mounts, queues, or credentials.
The file contains table-driven state, with roughly 3 initializer blocks controlling argument combinations, expected errnos, flags, or variants.

## State and Persistence
Persistent or externally visible state includes POSIX message queue objects and notification registration; child/thread synchronization and signal-observed outcomes. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `mq_notify` syscall test directory. POSIX message queues, tst_safe_posix_ipc, common mq helpers, signal/thread notification, pthread and realtime linkage.

## Risks
Risks: main risk is environment-specific syscall behavior causing TCONF or errno differences rather than source-level state corruption.

## Test Signals
negative paths validate exact errno or unexpected-success handling.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mq_notify/mq_notify02.c -->
