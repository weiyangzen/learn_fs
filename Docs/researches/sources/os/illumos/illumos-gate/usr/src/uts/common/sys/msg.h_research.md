# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/msg.h

Public System V message queue ABI header.

Key responsibilities:
- Defines message queue permission bits, wait-mode bits, and `MSG_NOERROR`.
- Defines `msgqnum_t`, `msglen_t`, and public `struct msqid_ds` with permissions, queue head/tail pointers, byte/message counts, byte limit, last sender/receiver PIDs, timestamps, and reserved fields.
- Provides LP64/ILP32 timestamp padding for ABI compatibility.
- Defines user message buffer templates, using `_mtype/_mtext` under X/Open namespace rules.
- Defines `msgsnap()` buffer header and per-message header structures.
- Declares userland message queue APIs: `msgctl`, `msgget`, `msgids`, `msgsnap`, `msgrcv`, and `msgsnd`.

Dependencies:
- Includes `sys/ipc.h`.

Notable risks:
- This is public ABI; struct layout, padding, and namespace-sensitive field names must remain stable.
- Kernel code uses a different internal message buffer name to avoid collisions.
