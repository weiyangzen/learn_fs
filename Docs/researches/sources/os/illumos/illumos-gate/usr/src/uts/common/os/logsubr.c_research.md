# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/logsubr.c

## Purpose

`logsubr.c` implements core kernel logging support for `/dev/log`, `/dev/conslog`, console/backlog queues, recent console message buffers, message allocation/recycling, zone-specific log clone state, and dispatch of kernel log messages to interested readers.

It is the common backend used by console logging, syslog-facing queues, panic-time message handling, and per-zone `/dev/log` clones.

## Global State

Important queues:

- `log_consq`: current console queue.
- `log_backlogq`: backlog queue used before a console reader exists.
- `log_intrq`: high-level interrupt message queue.
- `log_recentq`: recent console message buffer.
- `log_freeq`: reusable message block queue.

Important objects:

- `log_global`: global-zone log state.
- `log_backlog`: synthetic backlog log endpoint.
- `log_minorspace`: clone minor ID allocator.
- `log_cons_cache`: cache for `/dev/conslog` log structures.
- `log_zone_key`: zone-specific storage key.

`log_seq_no[]` tracks sequence numbers by log stream flag.

## Locking

`log_enter()` and `log_exit()` wrap logging operations with `log_rwlock`. The lock is writer-only in this file and supports recursive entry by the current thread through `log_rwlock_depth`. This allows grouped logging, such as multiline `printf()`, to remain ordered and non-interleaved.

## Initialization

`log_init()` creates the backlog/console queue, free-message queue, interrupt queue, recent-message queue, minor ID space, zone-specific storage key, backlog log structure, and conslog cache. It then activates console logging via `log_update()` and prints the boot banner.

`log_makeq()` creates minimal STREAMS queues sufficient for `canput()`, `putq()`, and `getq_noenab()`, with `QNOENB` so queues are never service-enabled.

Zone state is initialized by `log_zoneinit()` and freed by `log_zonefree()`. Each zone gets preallocated `/dev/log` clone records and minor numbers.

## Device Allocation

`log_alloc()` handles clone allocation:

- `LOG_CONSMIN`: allocate a write-only `/dev/conslog` structure from `log_cons_cache` and a fresh minor.
- `LOG_LOGMIN`: return an unused per-zone `/dev/log` clone from zone-specific storage.

`log_free()` releases a conslog minor and frees the conslog structure.

## Queue Updates And Backlog

`log_update()` updates a log endpoint’s queue, flags, and filter callback, then recomputes active message types for the target zone. For global-zone console readers, it updates `log_consq`.

When the primary console queue switches between the backlog and a real reader, `log_conswitch()` moves messages between queues. It marks moved messages `SL_LOGONLY` and repairs early boot timestamps that were recorded before reliable `hrestime` was available.

`log_flushq()` drains a queue by sending each message through `log_sendmsg()`.

## Filtering

Filter callbacks include:

- `log_error()`: selects error messages and normalizes kernel facility priority to error.
- `log_trace()`: matches trace IDs against `log_data` records and normalizes matching kernel messages to debug priority.
- `log_console()`: maps internal console flags to syslog priorities.

## Message Allocation

`log_makemsg()` creates a two-block STREAMS message: an `M_PROTO` header containing `log_ctl_t` and a continuation block containing the NUL-terminated text. It reuses `log_freeq` blocks for small messages when possible, including interrupt context, and avoids sleeping in interrupt paths.

`log_freemsg()` returns suitable small messages to `log_freeq` unless the free queue is full; otherwise it frees the message.

## Message Dispatch

`log_sendmsg()` is the central dispatcher. It:

1. Resolves the target zone’s log state.
2. Drops messages if no active endpoint wants their flags.
3. Marks panic-created messages and increases console queue high-water mark during panic.
4. Detects and later fills `FACILITY_AND_PRIORITY` placeholders.
5. Sets lbolt and wall-clock timestamps.
6. Updates sequence counters.
7. Sends copies to backlog and `/dev/log` clones whose flags and filter callbacks match.
8. Emits overflow warnings when a destination queue cannot accept messages.
9. Prints kernel console messages directly when needed.
10. Stores recent console messages in `log_recentq`.
11. Frees the original message.

Global-zone messages go to the backlog first, then clones. Non-global-zone messages go only to that zone’s clones.

Console fallback printing occurs if there is no copy for the console queue, the console queue is still backlog, or the system is panicking, provided `SL_LOGONLY` is not set.

## Panic/Console Printing

`log_printq()` prints queued messages directly to the console, skipping panic messages already displayed. It walks queue chains from tail to head order, strips message IDs when present, and uses `console_printf()` to avoid re-queueing through the logging system.

## Cache Constructors

`log_cons_constructor()` initializes `/dev/conslog` log objects as global-zone conslog devices.

`log_cons_destructor()` asserts the object is still a global-zone conslog with no attached data.

## Dependencies

Depends on STREAMS queues and message blocks, zones and zone-specific data, syslog priority/facility constants, console output, boot banner support, id spaces, kmem caches, time/lbolt functions, panic state, and kernel string formatting.

## Research Notes

Important invariants are recursive logging lock depth correctness, safe interrupt-context allocation, backlog-to-console timestamp repair, zone-specific clone isolation, queue overflow behavior, panic-time direct console output, placeholder priority rewriting, and ensuring log message copies are freed or queued exactly once.
