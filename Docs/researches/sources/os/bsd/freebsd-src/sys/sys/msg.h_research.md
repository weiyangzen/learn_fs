# File Research: sources/os/bsd/freebsd-src/sys/sys/msg.h

Defines System V message queue ABI and kernel-private queue structures.

Key content:
- Defines `MSG_NOERROR`.
- Typedefs `msglen_t` and `msgqnum_t`.
- Declares standard scalar types if not already declared.
- Legacy `struct msqid_ds_old` is available under old FreeBSD compatibility options.
- `struct msqid_ds` exposes queue permissions, first/last message pointers, byte count, message count, byte limit, last send/receive pids, and send/receive/change times.
- Kernel-only `struct msg` stores next pointer, message type, message size, buffer segment location, and MAC label.
- Internal `struct msginfo` stores SysV tunables: max chars/message, queue identifiers, queue bytes, total messages, segment size, segment count.
- `struct msqid_kernel` wraps user-visible `msqid_ds` plus kernel-private MAC label and creator credentials.
- Kernel declares global `msginfo` and `kern_get_msqids`.
- Userland declares `msgctl`, `msgget`, `msgrcv`, and `msgsnd`.

Research relevance:
- IPC ABI with MAC integration and credential ownership.
- Relevant to kernel object accounting/security and compatibility, though not filesystem-specific.

Cautions:
- Header comments call out namespace pollution around `struct msg` and nonstandard members.
- Segment size constraints are documented but enforced in implementation.
