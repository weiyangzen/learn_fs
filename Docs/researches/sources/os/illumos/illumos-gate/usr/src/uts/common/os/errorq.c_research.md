# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/os/errorq.c

## Purpose

Implements kernel error queues: preallocated, panic-aware queues for hardware/error events that may be produced from high interrupt context and later drained safely by soft interrupt, explicit drain, or panic handling.

## Main Responsibilities

- Creates fixed-size error queues with `errorq_create()` and nvlist-backed queues with `errorq_nvcreate()`.
- Dispatches copied error payloads with `errorq_dispatch()`.
- Supports reserve/fill/commit/cancel workflows through `errorq_reserve()`, `errorq_commit()`, and `errorq_cancel()`.
- Drains queues in chronological order with `errorq_drain()`.
- Drains vital and nvlist queues during panic with `errorq_panic()`.
- Writes queued nvlist ereports into the dump file via `errorq_dump()`.
- Publishes per-queue kstats for dispatched, dropped, logged, reserved, failed, committed, and cancelled counters.

## Key Data Structures

- `errorq_t`: queue descriptor with element array, payload buffer, free bitmap, pending list, processing list, panic dump list, soft interrupt id, lock, flags, kstat, and global-list linkage.
- `errorq_elem_t`: queue element containing list pointers and a pointer into the preallocated payload region.
- `errorq_nvelem_t`: nvlist queue element wrapper, with a fixed-buffer nvlist allocator and nvlist pointer.
- `errorq_kstat_template`: named kstat layout copied into each queue.

## Queue Model

- Free elements are tracked by `eq_bitmap`.
- Producers never allocate memory in dispatch/commit paths; they claim a bitmap slot atomically.
- Pending errors are a singly-linked LIFO list through `eqe_prev`.
- Drainers reverse pending order into a processing list so callbacks see oldest-to-newest order.
- Nvlist queues preserve panic-drained elements on `eq_dump` rather than freeing them, so crash dump code can serialize ereports later.

## Important Control Flow

- `errorq_create()` allocates all queue state, registers a fixed soft interrupt when possible, creates kstats, initializes element data pointers, and links the queue into `errorq_list`.
- Early boot queues may be created before soft interrupt registration is possible; `errorq_init()` later registers missing softints and drains early events.
- `errorq_dispatch()`:
  - drops if queue is inactive,
  - atomically claims a free element,
  - copies and zero-pads payload,
  - pushes the element onto `eq_pend` with CAS,
  - optionally triggers the queue soft interrupt.
- `errorq_drain()`:
  - serializes consumers with `eq_lock`,
  - CAS-moves `eq_pend` to processing state,
  - builds forward links for chronological traversal,
  - invokes `eq_func(private, data, elem)`,
  - frees elements or appends nvlist elements to the dump list during panic.
- `errorq_panic_drain()` repairs each intermediate state possible if panic interrupts a normal drain, then logs all visible elements and invokes `errorq_drain()` for newly pending errors.
- `errorq_panic()` drains vital non-nvlist queues first, optionally nonvital queues, then vital nvlist queues, then nonvital nvlist queues.

## Panic and Ordering Guarantees

- The file documents and implements at-least-once callback semantics.
- Memory barriers make processing-list state visible to panic code in a recoverable order.
- If panic occurs during callback execution, the same error may be logged again; callbacks are expected to be repeat-safe.
- `errorq_vitalmin` prevents nonvital queues from consuming panic-time attention when many vital errors were logged.

## Nvlist/Ereport Support

- `errorq_nvcreate()` embeds `errorq_nvelem_t` at the front of each element data area and creates fixed-buffer FMA nvlist allocators.
- `errorq_elem_nvl()` and `errorq_elem_nva()` expose the nvlist and allocator for a reserved element.
- `errorq_dump()` packs each nvlist on `eq_dump`, wraps it with `erpt_dump_t`, computes checksum, timestamps relative to panic time, and writes with `dumpvp_write()`.

## External Interfaces and Dependencies

- Public kernel interfaces: `errorq_create()`, `errorq_nvcreate()`, `errorq_destroy()`, `errorq_dispatch()`, `errorq_drain()`, `errorq_init()`, `errorq_panic()`, `errorq_reserve()`, `errorq_commit()`, `errorq_cancel()`, `errorq_dump()`, `errorq_elem_nvl()`, `errorq_elem_nva()`, `errorq_elem_dup()`.
- Depends on atomic bitmap operations, soft interrupts, kstats, panic state, FMA nvlist utilities, dump headers, checksum, and `dumpvp_write()`.

## Notable Edge Cases

- Global `errorq_lost` counts errors sent to inactive/uninitialized queues.
- `errorq_availbit()` uses a rotor to spread allocations across elements for post-mortem diagnosis.
- `errorq_destroy()` disables the queue before draining and requires callers to prevent concurrent producers at a higher layer.
- `errorq_elem_dup()` only supports non-nvlist queues.
