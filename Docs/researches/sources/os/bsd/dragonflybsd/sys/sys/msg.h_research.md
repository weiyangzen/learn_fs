# File Research: sources/os/bsd/dragonflybsd/sys/sys/msg.h

System V message queue ABI header.

Key responsibilities:
- Defines `MSG_NOERROR`, `msglen_t`, `msgqnum_t`, and required scalar typedef guards.
- Defines public `struct msqid_ds` for queue permissions, first/last message links, byte/message counts, limits, sender/receiver PIDs, and timestamps.
- Defines BSD-visible example `struct mymsg` with message type and one-byte body placeholder.
- Defines kernel-visible `struct msginfo` tunables.
- Declares userland `msgctl`, `msgget`, `msgsnd`, and `msgrcv`, or kernel `msginfo`.

Important behavior:
- Comments note kernel and userland implementations historically differ in how message links are interpreted.
- `msgrcv` is declared as returning `int` with an XXX note that it should return `ssize_t`.

Dependencies:
- Includes `sys/cdefs.h`, `sys/ipc.h`, and `machine/stdint.h`.

Notable risks:
- `struct msqid_ds` layout is ABI-sensitive for SysV IPC tools and libc.
- The historical `msgrcv` return type mismatch is compatibility-sensitive.
- Pointer fields in `msqid_ds` are not meaningful as stable userland object references.
