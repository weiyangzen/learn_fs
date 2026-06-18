# File Research: sources/os/bsd/netbsd-src/sys/kern/sysv_msg.c

## Purpose

`sysv_msg.c` implements NetBSD's System V message queue facility: queue creation/removal, message send/receive, queue metadata control, permission checks, blocking semantics, and runtime resizing of selected IPC limits.

## Main Responsibilities

- Initializes and tears down the global SysV message subsystem.
- Maintains message queue descriptors, message headers, segment maps, and the message byte pool.
- Implements `msgget`, `msgsnd`, `msgrcv`, and `msgctl`.
- Supports compatibility entry points through `msgsnd1`, `msgrcv1`, and `msgctl1`.
- Enforces `ipc_perm` permissions and privileged queue-size increases through kauth.
- Exposes writable `kern.ipc.msgmni` and `kern.ipc.msgseg` sysctls.

## Core Data Model

The subsystem allocates one wired block containing `msgpool`, `msgmaps`, `msghdrs`, and `msqs`. Message bodies are stored as chains of fixed-size segments indexed by `struct msgmap`; message metadata lives in `struct __msg` headers. Each queue is a `kmsq_t` containing `struct msqid_ds` plus a condition variable.

Queue IDs combine an array index with the queue sequence number, so stale IDs fail sequence validation after reuse.

## Send and Receive Behavior

`msgsnd1()` validates ID, sequence, permissions, and message type, then waits until the queue has room, free segment maps, and a free message header. While copying from user memory it marks the queue `MSG_LOCKED` so the descriptor is not reused mid-copy. On success it appends the message, updates byte/message counts, sender PID, timestamp, and wakes waiters.

`msgrcv1()` selects either the first message, an exact type, or the first type less than or equal to `abs(msgtyp)` for negative type requests. It honors `IPC_NOWAIT`, `MSG_NOERROR`, and sequence changes after sleeps. Bookkeeping is updated before copying to user memory, then the message header and segments are returned to the free lists.

## Control and Resizing

`msgctl1()` handles `IPC_STAT`, `IPC_SET`, and `IPC_RMID`. Removal frees all queued messages, marks the slot free by setting `msg_qbytes` to zero, and wakes sleepers.

`msgrealloc()` allocates a new wired layout, marks a global reallocation state, wakes and drains receive/send waiters, verifies the new limits can hold existing queues and segments, copies live queues/messages into the new arrays, swaps the global pointers, and frees the old block.

## Concurrency Notes

`msgmutex` protects all global message state. Per-queue condition variables coordinate senders/receivers. `msg_waiters`, `msg_realloc_state`, and `msg_realloc_cv` coordinate sysctl resizing with sleepers so waiters restart against the new arrays rather than retaining stale pointers.
