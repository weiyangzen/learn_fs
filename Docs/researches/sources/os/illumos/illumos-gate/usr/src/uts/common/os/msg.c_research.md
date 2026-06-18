# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/msg.c

## Purpose

`msg.c` implements the illumos System V message queue facility. It provides the loadable syscall module for `msgget`, `msgctl`, `msgsnd`, `msgrcv`, `msgids`, and `msgsnap`, with per-zone/project resource control integration and scalable waiter wakeup logic.

Read completely: 1,584 lines.

## Main Responsibilities

- Registers the System V message syscall module and 32-bit syscall entry points.
- Creates and destroys IPC service state for message queue IDs.
- Allocates, initializes, removes, and destroys message queues.
- Implements permission checks, resource controls, auditing hooks, and zone cleanup.
- Sends messages with bounded byte and message-count limits.
- Receives messages by type semantics, including exact, any, and negative type selection.
- Provides message queue snapshots without consuming messages.
- Avoids receiver thundering-herd wakeups through targeted waiter queues.

## Key Data Structures And Globals

- `msq_svc`: IPC service for message queues.
- `msg_zone_key`: zone cleanup key.
- `kmsqid_t`: per-message-queue kernel state, including message list, byte counts, qbytes/qmax limits, wait lists, receiver/sender counts, and selection rotors.
- `struct msg`: queued message with type, size, payload pointer, flags, reference/copy count, and list linkage.
- `msgq_wakeup_t`: stack-allocated waiter record with thread, condition variable, message type/size, and wake metadata.
- `msg_fnd_sndr`: rotating selector array for type-0, exact positive, and negative receive waiters.
- `msg_fnd_rdr`: selector for copyout waiters.

## Module Lifecycle

`_init()` creates the IPC service with `ipcs_create()`, registers a zone cleanup callback, and installs the syscall module. `_fini()` always returns `EBUSY`, so the module is not unloadable. `_info()` delegates to `mod_info()`.

`msg_dtor()` asserts and destroys all queue lists. `msg_rmid()` removes all messages, wakes every receiver/sender/copyout waiter, and leaves the object ready for IPC destruction. `msg_remove_zone()` removes all queues associated with a halted zone.

## Queue Creation And Control

`msgget()` uses common IPC allocation/lookup code. For new queues, it initializes message and waiter lists, receiver/sender counters, negative-message metadata, selection rotors, and resource-control-derived limits for queue bytes and message count.

`msgctl()` handles `IPC_SET`, `IPC_STAT`, `IPC_SET64`, `IPC_STAT64`, and `IPC_RMID`. It performs copyin before lookup where needed, enforces privilege/resource-control checks for increasing `msg_qbytes`, updates IPC permissions and timestamps, and copies status out after releasing the queue lock.

`msgids()` delegates ID enumeration to common IPC code.

## Send Path

`msgsnd()` copies the message type, validates that it is positive, and preallocates small messages up to `MSG_PREALLOC_LIMIT` before taking the queue lock. Larger messages are allocated and copied outside the queue lock after space is available, then the function revalidates the queue and retries.

If the queue lacks byte space or has reached `msg_qmax`, senders either fail with `EAGAIN` under `IPC_NOWAIT` or enqueue on `msg_wait_rcv`. `msg_wakeup_senders()` scans waiting senders in order, waking those whose sizes can fit into the available projected space.

On successful send, the message is appended, queue byte/message counters and send metadata are updated, the lowest message type hint is adjusted, and `msg_wakeup_rdr()` wakes a matching receiver.

## Receive Path

`msgrcv()` looks up the queue, checks read permission, and repeatedly searches for a matching message through `msgrcv_lookup()`:

- `msgtyp == 0`: first message.
- `msgtyp > 0`: first message with exact type, with a low-type hint fast rejection.
- `msgtyp < 0`: lowest type less than or equal to `-msgtyp`, with negative-copy serialization.

`msg_copyout()` marks a message `MSG_RCVCOPY`, holds a reference, releases the queue lock, copies type and text to userland, reacquires the lock, clears copy state, handles queue deletion, unlinks the message on success, and wakes senders through `msgunlink()`.

If no message matches, receivers fail with `ENOMSG` under `IPC_NOWAIT` or sleep on either positive/zero `msg_wait_snd` buckets or negative `msg_wait_snd_ngt` buckets. If a matching message is already being copied out, receivers sleep on `msg_cpy_block` and restart lookup after wakeup.

## Waiter Selection And Hashing

`msg_type_hash()` maps type zero to bucket 0, positive types to hashed buckets 1..`MSG_MAX_QNUM`, and negative type ranges to interval buckets capped at `MSG_MAX_QNUM`.

`msg_wakeup_rdr()` rotates through selector functions to avoid starving any class of receiver. The selectors find:

- any-message receivers,
- exact positive type receivers,
- eligible negative type receivers,
- copyout waiters.

Negative receiver selection randomizes its starting bucket using the queue's last send time within the eligible range. `msg_rcvq_sleep()` inserts a stack waiter, waits interruptibly, relocks the IPC object, decrements receiver count, and removes itself on unexpected wakeup.

## Snapshot Path

`msgsnap()` computes required buffer size and matching message count, optionally holds references to matching messages, releases the lock, copies out a snapshot header and per-message headers/payloads with native or 32-bit alignment, then drops holds while checking for queue deletion.

If the provided buffer is too small, it reports the required size and zero messages rather than copying payloads.

## Resource Controls And Compatibility

The preferred limits are resource controls:

- `zone.max-msg-ids`
- `project.max-msg-ids`
- `process.max-msg-qbytes`
- `process.max-msg-messages`

Obsolete `msginfo_*` tunables remain declared for compatibility. The module also provides 32-bit syscall wrappers on LP64 kernels, including 32-bit message type conversion.

## Notable Edge Cases

- Message payload copyout occurs without the queue lock to prevent denial of service from slow user memory.
- `MSG_RCVCOPY` and the copyout waiter chain prevent multiple receivers from consuming or indefinitely blocking on the same message.
- Negative receive lookup uses `msg_neg_copy` and a static sentinel to serialize negative-type copyout cases.
- `msgsnd()` must redo space checks after large-message copyin because the lock was dropped.
- `msg_wakeup_senders()` projects byte space and message slots as if awakened senders will succeed.
- Queue deletion during waits or copy operations returns `EIDRM`.

## Research Relevance

This file is core IPC rather than filesystem code, but it is important OS infrastructure. Filesystem daemons, test harnesses, and storage management tools may rely on System V IPC behavior; the implementation also demonstrates illumos IPC locking, resource controls, zone cleanup, and copyin/copyout patterns.
