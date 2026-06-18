# File Research: sources/os/bsd/netbsd-src/sys/kern/subr_ipi.c

Read completely: 453 lines.

Implements the MI inter-processor interrupt interface. It provides asynchronous registered IPI handlers and synchronous message-based IPIs built on reserved handler slot zero.

Core behavior:
- `ipi_sysinit()` initializes handler slots and reserves `IPI_SYNCH_ID` for mailbox messages.
- `ipi_register()`/`ipi_unregister()` allocate asynchronous handler IDs; unregister broadcasts a no-op synchronous IPI to drain in-flight calls.
- Per-CPU pending bitfields record asynchronous IPIs; `ipi_cpu_handler()` atomically drains and invokes handlers.
- `ipi_unicast()`, `ipi_multicast()`, and `ipi_broadcast()` enqueue `ipi_msg_t` pointers into per-CPU cache-line mailboxes and trigger the synchronous IPI.
- `ipi_wait()` spin-waits until remote CPUs decrement the message pending count.

Concurrency and risks:
- Triggering requires preemption disabled for multi/broadcast paths.
- Mailboxes have a fixed number of slots and spin with an event counter when full.
- `ipi_multicast()` executes the local handler directly but only waits for remote acknowledgements.
