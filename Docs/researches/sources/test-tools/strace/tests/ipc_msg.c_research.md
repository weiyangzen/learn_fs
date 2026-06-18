<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/tests/ipc_msg.c -->
# sources/test-tools/strace/tests/ipc_msg.c

Purpose: Tests SysV message queue syscall decoding for `msgget` and `msgctl` commands, including metadata structures and Linux-specific info/stat commands.

Important APIs/types/functions: Uses `msgget`, `msgctl`, `struct msqid_ds`, `struct msginfo`, `atexit`, `cleanup`, `print_msginfo`, `print_msqid_ds`, and xlat strings for resource flags and IPC/msg commands.

Control flow: It prints a bogus `msgget`, creates a private queue, registers cleanup, optionally tests bogus commands and bogus addresses depending on glibc/version guards, reads and sets `IPC_STAT`/`IPC_SET`, prints `IPC_INFO`, `MSG_INFO`, `MSG_STAT`, and `MSG_STAT_ANY` when available, then cleanup removes the queue.

State/persistence behavior: Creates one private message queue and removes it via `atexit(cleanup)`. State persists only for the test process lifetime; cleanup output is part of expected matching.

Dependencies: Depends on SysV message queue support, glibc behavior guards, `resource_flags` xlat data, and raw/verbose/abbrev macro variants.

Integration points: Validates strace SysV message decoders, regex-friendly expected output via escaped parentheses/braces, IPC_64 optional rendering, time/permission fields, and command xlat modes.

Risks: libc may intercept invalid commands or dereference bogus pointers on some ABIs; the compile-time guards intentionally skip unsafe cases. Kernel limits and permissions may affect info commands.

Test signals: Expected output includes queue creation/removal, decoded permissions, message stats, optional bogus command/address lines, and xlat-mode-specific command names.

Source read signal: complete file read for this research pass; file size 263 line(s), 7690 byte(s).
<!-- END_FILE_RESEARCH: sources/test-tools/strace/tests/ipc_msg.c -->
