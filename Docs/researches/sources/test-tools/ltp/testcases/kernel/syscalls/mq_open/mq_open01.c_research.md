<!-- BEGIN_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mq_open/mq_open01.c -->
# sources/test-tools/ltp/testcases/kernel/syscalls/mq_open/mq_open01.c

## Purpose
This file mq_open matrix covering creation, attributes, long names, access, exclusivity, file descriptor limits, missing queues, and queues_max.
The source-level description states or implies: Copyright (c) Crackerjack Project., 2007-2008 ,Hitachi, Ltd Author(s): Takahiro Yasui <takahiro.yasui.mp@hitachi.com>, Yumiko Sugita <yumiko.sugita.yf@hitachi.com>, Satoshi Fujiwara <sa-fuji@sdl.hitachi.co.jp> Copyright (c) 2016 Linux Test Project

## Important APIs, Types, and Functions
Key local functions: `create_queue()`, `unlink_queue()`, `set_rlimit()`, `restore_rlimit()`, `set_max_queues()`, `restore_max_queues()`, `create_queue()`, `unlink_queue()`, `set_max_queues()`, `restore_max_queues()`, `set_rlimit()`, `restore_rlimit()`, `setup()`, `cleanup()`, `do_test()`.
Primary syscall/API surface: `mq_open`, `mq_unlink`.
LTP and helper APIs used include: `SAFE_CLOSE`, `SAFE_FILE_PRINTF`, `SAFE_FILE_SCANF`, `SAFE_GETPWNAM`, `SAFE_GETRLIMIT`, `SAFE_MQ_OPEN`, `SAFE_SETEUID`, `SAFE_SETRLIMIT`, `TEST`, `mq_attr`, `mq_close`, `mq_getattr`, `mq_maxmsg`, `mq_msgsize`, `mq_open`, `mq_unlink`, `tst_brk`, `tst_res`, `tst_safe_file_ops`, `tst_safe_posix_ipc`, `tst_test`.
Harness fields present in `struct tst_test`: `.cleanup`, `.needs_root`, `.setup`, `.tcnt`, `.test`.

## Control Flow
The modern LTP harness enters through `.test` after optional `.setup`; it runs one case or iterates `.tcnt` table entries, records results with `tst_res`/`TST_EXP_*`, and then invokes `.cleanup` for mapped memory, descriptors, mounts, queues, or credentials.
The file contains table-driven state, with roughly 16 initializer blocks controlling argument combinations, expected errnos, flags, or variants.

## State and Persistence
Persistent or externally visible state includes POSIX message queue objects and notification registration; effective uid changes between root and nobody; temporary files, file descriptors, or LTP temp directories. Cleanup paths are part of the test contract because leaked mappings, mounts, queues, credentials, or sysfs values would affect later LTP cases.

## Dependencies and Integration Points
This file belongs to the `mq_open` syscall test directory. POSIX message queues, /proc/sys/fs/mqueue/queues_max, RLIMIT_NOFILE, root/nobody credentials, and mqueue cleanup.

## Risks
Risks: requires privilege and may produce misleading failures if user switching or capability assumptions differ; temporarily changes resource limits or kernel control files and must restore them.

## Test Signals
explicit TPASS/TST_EXP_PASS checks mark expected syscall behavior; negative paths validate exact errno or unexpected-success handling.
<!-- END_FILE_RESEARCH: sources/test-tools/ltp/testcases/kernel/syscalls/mq_open/mq_open01.c -->
