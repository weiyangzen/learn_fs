# File Research: sources/os/bsd/dragonflybsd/sys/kern/sysv_msg.c

## Summary
Implements SVID/System V message queues. It maintains fixed-size pools of queue descriptors, message headers, message-map segments, and message data storage, and exposes `msgctl`, `msgget`, `msgsnd`, and `msgrcv`.

## Main Responsibilities
- Initializes global SysV message pools and validates segment sizing in `msginit()`.
- Tracks free message-map segments and free message headers.
- Frees message headers and their segment chains with `msg_freehdr()`.
- Implements `sys_msgctl()` for `IPC_RMID`, `IPC_SET`, and `IPC_STAT`.
- Implements `sys_msgget()` for keyed lookup and queue creation.
- Implements `sys_msgsnd()` for permission checks, resource waiting, segment allocation, user copyin, queue append, and wakeups.
- Implements `sys_msgrcv()` for type matching, optional blocking, truncation rules, user copyout, resource release, and wakeups.
- Exposes tunables/sysctls for message limits and a `msqids` sysctl dump.

## Important Behavior
All queue state is protected by a single `msg_token`. Message bodies are split into fixed-size `msgssz` segments linked through `msgmaps`; `msg_spot` points to the first segment. Queue IDs combine a table index with a sequence number to detect stale IDs.

`sys_msgsnd()` may sleep for queue bytes, free segments, free headers, or another sender/receiver's `MSG_LOCKED` copy window. Before copying from user memory, it marks the queue locked so the descriptor cannot be reused while the token may be temporarily lost during copy faults. `sys_msgrcv()` removes the selected message from the queue before copying it out and frees it even if copyout fails.

Message receive type rules support first-message (`msgtyp == 0`), exact positive type, and first type less than or equal to `-msgtyp`. `MSG_NOERROR` allows truncation to the caller's buffer size.

## Dependencies and Integration
This file uses `ipcperm()` from `sysv_ipc.c`, jail capability checks, process credentials, SysV IPC ID macros, sysctl/tunables, and sleep/wakeup primitives.

## Risks
The fixed global pools make resource exhaustion and wakeup ordering important. The single-token design serializes state but copyin/copyout paths can temporarily block, requiring `MSG_LOCKED` to avoid descriptor reuse races. As with historical SysV implementations, failed receive copyout can still consume a message because bookkeeping is done before user copies.
