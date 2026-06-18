# File Research: sources/os/bsd/freebsd-src/sys/kern/sysv_msg.c

## Purpose

`sysv_msg.c` implements FreeBSD System V message queues. It provides module initialization/unload, message queue allocation and removal, `msgctl`, `msgget`, `msgsnd`, `msgrcv`, sysctl visibility, jail scoping, MAC Framework hooks, RACCT accounting, and compatibility syscall wrappers.

It exposes the feature as:

- `FEATURE(sysv_msg, "System V message queues support")`
- Kernel module name: `sysvmsg`

## Core Data and Limits

The implementation stores message bodies in fixed-size segments and tracks them with header and map pools:

- `msgpool`: contiguous message data segment storage.
- `msgmaps`: segment free-list metadata.
- `msghdrs`: message header pool.
- `msqids`: message queue descriptor array.
- `msq_mtx`: global mutex for message queue state.
- `free_msgmaps`, `nfree_msgmaps`: free segment tracking.
- `free_msghdrs`: free message header list.

Default tunables and derived limits include:

- `MSGSSZ` default `8`
- `MSGSEG` default `2048`
- `MSGMAX = MSGSSZ * MSGSEG`
- `MSGMNB` default `2048`
- `MSGMNI` default `40`
- `MSGTQL` default `40`

`msginit()` validates that `msgssz` is a small power of two and that `msgseg <= 32767`.

Queue IDs are sequence/index encoded through macros such as `MSQID`, `MSQID_IX`, `MSQID_SEQ`, and FreeBSD IPC ID helpers used later in syscall paths.

## Module Lifecycle

`msginit()` allocates and initializes all global message queue pools, MAC labels, the mutex, jail OSD slot state, and syscall helper registrations.

`msgunload()` unregisters syscalls, refuses unload with `EBUSY` if any queue is active or locked, deregisters jail OSD state, destroys MAC labels, frees pools, and destroys `msq_mtx`.

`sysvmsg_modload()` dispatches module load/unload/shutdown events.

## Queue and Message Cleanup

`msg_freehdr(struct msg *msghdr)` releases all segments owned by a message header back to the segment free list, returns the header to `free_msghdrs`, and cleans MAC message state.

`msq_remove(struct msqid_kernel *msqkptr)` removes an entire queue:

- Subtracts RACCT counts and sizes from the queue credential.
- Releases the held credential.
- Frees every message header and its segments.
- Verifies `msg_cbytes` and `msg_qnum` reach zero.
- Sets `msg_qbytes = 0` to mark the queue slot free.
- Cleans MAC queue state.
- Wakes sleepers on the queue.

## Jail Scoping

System V message queues are jail-aware. The file uses an OSD jail slot, `msg_prison_slot`, to associate jails with a System V message queue root.

Key helpers:

- `msg_find_prison()` returns the queue root prison visible to a credential.
- `msq_prison_cansee()` permits visibility only when the queue credential prison matches the root prison or is a child.
- `msg_prison_check()`, `msg_prison_set()`, `msg_prison_get()`, and `msg_prison_remove()` implement jail parameter handling for `sysvmsg`.
- `msg_prison_cleanup()` removes queues owned by a jail when its independent System V message queue namespace is removed.

The jail parameter supports disabled, new, and inherited behavior, and legacy `allow.sysvipc` flags are mapped into this model.

## `msgctl`

`sys_msgctl()` handles user copyin/copyout around `kern_msgctl()`.

`kern_msgctl()` validates the queue ID and sequence, checks jail visibility, applies MAC checks, and implements:

- `IPC_RMID`: requires `IPC_M`, checks per-message MAC removal permissions, and calls `msq_remove()`.
- `IPC_SET`: requires `IPC_M`, checks privilege for increasing queue byte limits, caps to `msginfo.msgmnb`, rejects zero queue byte size, updates owner/group/mode/qbytes/ctime.
- `IPC_STAT`: requires `IPC_R`, returns queue metadata, hides keys across prison boundaries, and clears kernel pointers before returning to userland.

## `msgget`

`sys_msgget()` finds or creates queues.

Behavior:

- Rejects operation with `ENOSYS` if the caller has no visible System V message queue prison.
- For non-private keys, searches existing queues in the caller’s prison.
- Enforces `IPC_CREAT | IPC_EXCL`, permission checks, and MAC `msqget` checks.
- For creation, finds an unused and unlocked queue slot.
- Applies RACCT `RACCT_NMSGQ`.
- Initializes permissions, credential hold, sequence number, timestamps, byte limits, and queue pointers.
- Returns a sequence/index encoded IPC ID.

## `msgsnd`

`sys_msgsnd()` copies in the leading message type and delegates to `kern_msgsnd()`.

`kern_msgsnd()` performs:

- Jail visibility and queue ID/sequence validation.
- Write permission through `ipcperm(..., IPC_W)`.
- MAC queue send checks.
- RACCT reservation for queued message count and byte size.
- Resource checks for queue byte capacity, free segments, free headers, and `MSG_LOCKED`.
- Optional blocking with `msleep()` unless `IPC_NOWAIT` is set.
- Temporary queue locking with `MSG_LOCKED` while copying from userland.
- Segment allocation from `free_msgmaps`.
- Message type validation (`mtype >= 1`).
- Copyin of message body into `msgpool`.
- MAC message-to-queue enqueue check.
- Queue append, byte/count/pid/time accounting, wakeup, and return value setup.

On errors after RACCT reservation, it rolls back RACCT message count and size.

## `msgrcv`

`sys_msgrcv()` delegates to `kern_msgrcv()` and then copies out the returned message type.

`kern_msgrcv()` performs:

- Jail visibility and queue ID/sequence validation.
- Read permission through `ipcperm(..., IPC_R)`.
- MAC queue receive checks.
- Message selection:
  - `msgtyp == 0`: first message.
  - Positive `msgtyp`: exact type match.
  - Negative `msgtyp`: first message with type less than or equal to absolute value.
- Size enforcement with `MSG_NOERROR` truncation semantics.
- Optional blocking with `msleep()` unless `IPC_NOWAIT` is set.
- `EIDRM` detection if the queue is removed while sleeping.
- Queue unlink and bookkeeping before copyout.
- RACCT subtraction for queued message count and size.
- Segment-by-segment copyout from `msgpool`.
- Header/segment release through `msg_freehdr()`.
- Wakeup of senders and return of actual copied byte count.

## Visibility and Sysctls

`sysctl_msqids()` exports the queue array through `kern.ipc.msqids`, hiding entries invisible to the caller’s jail and clearing kernel pointers/labels/credentials before output.

`kern_get_msqids()` returns a sanitized allocated snapshot of queue descriptors for kernel consumers.

The file also exposes sysctls for:

- `kern.ipc.msgmax`
- `kern.ipc.msgmni`
- `kern.ipc.msgmnb`
- `kern.ipc.msgtql`
- `kern.ipc.msgssz`
- `kern.ipc.msgseg`
- `kern.ipc.msqids`

## Compatibility Paths

The file includes 32-bit and older FreeBSD ABI support when configured:

- 32-bit wrappers for `msgctl`, `msgsnd`, `msgrcv`, and legacy `msgsys`.
- Older `freebsd7_msgctl()` conversion paths.
- Legacy multiplexed `sys_msgsys()` dispatch through `msgcalls[]`.

These wrappers convert structure layouts and message type widths, then delegate to the native kernel implementations.

## Security and Correctness Notes

This file is concurrency- and security-sensitive. Important invariants include:

- `msq_mtx` protects global queue/message state.
- `MSG_LOCKED` prevents queue slot reuse and concurrent mutation while user copy operations may fault.
- Queue sequence numbers prevent stale IPC IDs from accessing recycled slots.
- `msg_qbytes == 0` marks a queue slot free.
- Kernel pointers are scrubbed before user-visible sysctl/stat export.
- MAC hooks are placed around queue operations and individual message operations.
- Jail namespace checks are required before exposing or operating on queues.
- RACCT reservations are rolled back on send failure and subtracted on receive/removal.

The main implementation risk areas are changes around sleep/retry paths, `MSG_LOCKED` handling, RACCT rollback, and sanitization of exported queue structures.
