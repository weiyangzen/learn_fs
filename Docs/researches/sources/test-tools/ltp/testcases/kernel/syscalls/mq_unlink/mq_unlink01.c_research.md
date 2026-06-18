<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mq_unlink/mq_unlink01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mq_unlink/mq_unlink01.c

## Purpose
This file mq_unlink matrix covering successful unlink, permission denial as nobody, missing long queue names, and ENAMETOOLONG.
The source-level description states or implies: Copyright (c) Crackerjack Project., 2007-2008 ,Hitachi, Ltd Author(s): Takahiro Yasui <takahiro.yasui.mp@hitachi.com>, Yumiko Sugita <yumiko.sugita.yf@hitachi.com>, Satoshi Fujiwara <sa-fuji@sdl.hitachi.co.jp> Copyright (c) 2016 Linux Test Project

## Important APIs, Types, and Functions
Key local functions: `setup()`, `do_test()`.
Primary syscall/API surface: `mq_unlink`.
LTP and helper APIs used include: `SAFE_GETPWNAM`, `SAFE_MQ_OPEN`, `TEST`, `mq_unlink`, `seteuid`, `tst_res`, `tst_safe_posix_ipc`, `tst_strerrno`, `tst_test`.
Harness fields present in `struct tst_test`: `.needs_root`, `.setup`, `.tcnt`, `.test`.

## Control Flow
The modern LTP harness enters through `.test` after optional `.setup`; it runs one case or iterates `.tcnt` table entries, records results with `tst_res`/`TST_EXP_*`, and then invokes `.cleanup` for mapped memory, descriptors, mounts, queues, or credentials.
The file contains table-driven state, with roughly 5 initializer blocks controlling argument combinations, expected errnos, flags, or variants.

## State and Persistence
Persistent or externally visible state includes POSIX message queue objects and notification registration; effective uid changes between root and nobody; child/thread synchronization and signal-observed outcomes; temporary files, file descriptors, or LTP temp directories. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `mq_unlink` syscall test directory. POSIX message queues, root/nobody credentials, long queue-name boundary cases, and mqueue cleanup.

## Risks
Risks: requires privilege and may produce misleading failures if user switching or capability assumptions differ.

## Test Signals
explicit TPASS/TST_EXP_PASS checks mark expected syscall behavior; negative paths validate exact errno or unexpected-success handling.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mq_unlink/mq_unlink01.c -->
