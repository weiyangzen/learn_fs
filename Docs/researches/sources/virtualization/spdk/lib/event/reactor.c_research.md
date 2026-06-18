# File Research: sources/virtualization/spdk/lib/event/reactor.c

Implements SPDK's reactor runtime: event queues, per-core reactor loops, SPDK thread scheduling, interrupt-mode support, scheduler/governor registration, and scheduler tracepoints.

Important behavior:
- Initializes one `struct spdk_reactor` per active env lcore with an event ring, optional eventfds/fd-group interrupt support, and a thread queue.
- Creates the global event mempool and initializes the SPDK thread library with reactor-specific thread operations.
- `spdk_event_allocate()` and `spdk_event_call()` enqueue cross-core events and notify interrupt-mode reactors when needed.
- Reactor loops run event batches, poll SPDK threads, update busy/idle TSC accounting, monitor context switches, and initiate periodic scheduler passes.
- Thread scheduling chooses a target lcore from the thread cpumask, round-robins via `g_next_core`, and respects interrupt-mode limitations.
- Supports thread reschedule requests and scheduler-driven migrations using `struct spdk_lw_thread`.
- `spdk_for_each_reactor()` serializes callbacks across all reactors and completes on the original reactor.
- Linux interrupt mode uses `eventfd` plus `spdk_fd_group` for event queue and reschedule notifications.
- Scheduler infrastructure registers, selects, initializes/deinitializes, runs balance phases, tracks isolated cores, and updates per-core interrupt modes.
- Governor infrastructure registers and selects CPU governors.
- Registers scheduler tracepoint descriptions for scheduler period start, core stats, thread stats, and thread moves.

Lifecycle notes:
- `spdk_reactors_start()` launches remote lcore reactor threads and runs the current-core reactor inline until stop.
- `spdk_reactors_stop()` schedules a final reactor iteration that sets state to exiting and wakes reactors.
- `spdk_reactors_fini()` requires all reactor thread queues to be empty before freeing rings, fd groups, mempool, and arrays.
