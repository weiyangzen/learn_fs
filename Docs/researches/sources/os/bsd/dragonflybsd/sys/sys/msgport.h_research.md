# File Research: sources/os/bsd/dragonflybsd/sys/sys/msgport.h

Core LWKT message and port interface for intra-kernel thread communication.

Key responsibilities:
- Defines opaque pointer typedefs `lwkt_msg_t` and `lwkt_port_t`.
- Defines `lwkt_msg_queue` as a TAILQ of messages.
- Defines `struct lwkt_msg` with queue linkage, target/reply ports, abort handler, flags, error, result union, and receipt callback.
- Defines message state flags: done, reply, queued, sync, in-transit, waiting, droppable, abortable, priority, receipt, and user command bits.
- Defines `struct lwkt_port` with normal/priority queues, flags, CPU id, synchronization union, owning thread, and port operation callbacks.
- Declares kernel port initialization and message send/forward/abort APIs.

Important behavior:
- Message ownership is explicit: only the current owner should manipulate a message.
- Synchronous messages may wake waiters directly instead of being queued on reply.
- Thread ports and spin/descriptor ports use different fields in the port union and have different ownership expectations.
- High 16 message-flag bits are available to handlers and also define CDEV/VFS/SYSCALL command namespaces.

Dependencies:
- Includes `queue.h`, `spinlock.h`, and machine integer types.
- Kernel section depends on `boolean_t`, `struct thread`, `struct spinlock`, and `struct lwkt_serialize`.

Notable risks:
- Port callbacks define the semantics; incorrect `mp_putport`, `mp_replyport`, or `mp_dropmsg` implementations can break sync/async completion.
- Message flags are manipulated by owners only; cross-owner mutation is a race.
- Dropping is only supported by certain embedded/thread ports and must be done in the port owner thread.
