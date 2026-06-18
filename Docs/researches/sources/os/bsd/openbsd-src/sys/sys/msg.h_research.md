# File Research: sources/os/bsd/openbsd-src/sys/sys/msg.h

Defines System V message queue ABI and kernel queue implementation structures.

Key contents:
- Public `MSG_NOERROR`, `msgqnum_t`, `msglen_t`, and `struct msqid_ds`.
- Kernel `struct msg`, `struct que`, queue flags, and reference macros `QREF`/`QRELE`.
- `struct msginfo` configuration and sysctl export wrapper.
- Defaults for `MSGSSZ`, `MSGSEG`, `MSGMAX`, `MSGMNB`, `MSGMNI`, and `MSGTQL`.

Key APIs:
- Kernel: `msginit()`, `sysctl_sysvmsg()`.
- Userland: `msgctl`, `msgget`, `msgsnd`, `msgrcv`.

Risk notes:
- Message storage uses mbufs in-kernel, tying SysV IPC behavior to network-buffer allocation pressure.
