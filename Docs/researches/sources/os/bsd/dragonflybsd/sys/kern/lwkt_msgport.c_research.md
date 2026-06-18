# File Research: sources/os/bsd/dragonflybsd/sys/kern/lwkt_msgport.c

## Scope

This file implements the LWKT message-port abstraction: asynchronous and synchronous message submission, replies, forwarding, abort handling, and multiple backend implementations for thread-owned, spinlocked, serializer-protected, reply-only, put-only, and panic ports.

## Public And Internal APIs Covered

- Message lifecycle: `lwkt_sendmsg()`, `lwkt_sendmsg_oncpu()`, `lwkt_sendmsg_prepare()`, `lwkt_sendmsg_start()`, `lwkt_sendmsg_start_oncpu()`, `lwkt_domsg()`, `lwkt_forwardmsg()`, `lwkt_abortmsg()`.
- Port initialization: `lwkt_initport_thread()`, `lwkt_initport_spin()`, `lwkt_initport_serialize()`, `lwkt_initport_replyonly_null()`, `lwkt_initport_replyonly()`, `lwkt_initport_putonly()`, `lwkt_initport_panic()`.
- Queue helpers: `_lwkt_pushmsg()`, `_lwkt_pullmsg()`, `_lwkt_pollmsg()`, `_lwkt_enqueue_reply()`.
- Backend vectors for thread, spin, serializer, null, and panic ports.

## Control Flow And Behavior

- `lwkt_sendmsg()` clears reply/sync/done flags and invokes the target port put operation. If the target completes synchronously instead of returning `EASYNC`, it immediately queues a reply through `lwkt_replymsg()`.
- `lwkt_domsg()` marks `MSGF_SYNC`, submits the message, and either waits for an asynchronous reply or marks the message done when the target completed inline.
- `lwkt_forwardmsg()` forwards a not-queued, not-done, not-reply message to another target without rewriting send flags.
- `lwkt_abortmsg()` runs a caller-supplied abort callback only when `MSGF_ABORTABLE` is still set and the message has not already completed or replied.
- Message ports maintain normal and priority queues. `_lwkt_pollmsg()` always returns priority work first.
- `_lwkt_pushmsg()` sets `MSGF_QUEUED`, inserts into the selected queue, and invokes receipt callbacks once by clearing `MSGF_RECEIPT`.
- Thread ports assume one owning thread. Cross-CPU puts/replies are delivered by IPI to the owning thread's current CPU, chasing migrations until `td_gd == mycpu`.
- Thread-port synchronous replies can avoid queueing by setting `MSGF_DONE | MSGF_REPLY` and scheduling the waiter if needed.
- Spin ports protect queues and wait flags with `mpu_spin`, support multiple waiters, and wake either the port or message depending on synchronous/asynchronous mode.
- `lwkt_spin_putport_oncpu()` asserts that fixed-CPU ports are used only from their assigned CPU and wakes with `wakeup_mycpu()`.
- Serializer ports require the caller to hold `mpu_serialize`; sleeps use `zsleep()` so the serializer is released/reacquired correctly around blocking.
- Panic ports intentionally trap illegal operations for restricted port types. The null reply port only marks messages done/replied.

## State And Data Structures

- Message flags drive protocol state: `MSGF_DONE`, `MSGF_QUEUED`, `MSGF_REPLY`, `MSGF_SYNC`, `MSGF_PRIORITY`, `MSGF_RECEIPT`, `MSGF_ABORTABLE`, `MSGF_DROPABLE`, `MSGF_WAITING`, and debug-only `MSGF_INTRANSIT`.
- `lwkt_port` stores function vectors, queue heads, wait flags, optional owner thread, optional spinlock, optional serializer, and optional fixed CPU.
- `ms_reply_port`, `ms_target_port`, `ms_error`, receipt callback, abort callback, and queue links are updated by the backend implementations.

## Dependencies

- Depends on LWKT thread scheduling, IPI delivery, spinlocks, serializers, sleep/wakeup primitives, and message/port definitions from `sys/msgport2.h`.
- Used by kernel services that need structured request/reply handoff across threads or CPUs.

## Risks And Invariants

- `lwkt_sendmsg()` and `lwkt_domsg()` must not be used to forward already active messages because they rewrite `ms_flags`.
- Thread-port queue access is only safe on the owning thread/CPU or through IPI redirection.
- Spin-port wait flags can produce extra wakeups; the waking side clears `MSGPORTF_WAITING`.
- `MSGF_DROPABLE` messages cannot be waited on.
- Serializer ports rely on external serialization; using them without holding the serializer violates their locking contract.
