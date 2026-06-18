# File Research: sources/os/bsd/freebsd-src/sys/kern/kern_intr.c

## Purpose
Implements FreeBSD interrupt event management, interrupt handler registration/removal, interrupt threads, software interrupts, affinity control, interrupt dispatch, and interrupt statistics exposure.

## Main Elements
- `struct intr_event` instances are tracked in `event_list`; each event has handlers, optional interrupt thread, source callbacks, affinity state, and flags.
- `struct intr_thread` represents an ithread and tracks `IT_DEAD`, `IT_WAIT`, pending service, and waiting state.
- `intr_priority()` maps interrupt type flags to scheduler priorities.
- `intr_event_create()` / `intr_event_destroy()` allocate and destroy event objects.
- `_intr_event_bind()`, `intr_setaffinity()`, and `intr_getaffinity()` bind IRQs and/or ithreads to CPUs or cpusets.
- `intr_event_add_handler()` validates exclusive/sleepable rules, creates an ithread when needed, and inserts handlers by priority.
- `intr_event_remove_handler()`, suspend/resume, and barrier helpers coordinate safe handler removal with either lockless fast-path execution or ithread-mediated removal.
- `intr_event_handle()` is the hardware interrupt dispatch path: it runs filters in interrupt context, manages active counters/phases, invokes pre/post callbacks, and schedules ithreads when required.
- `ithread_loop()` services pending handlers, enters NET_EPOCH for network handlers, throttles interrupt storms, and re-enters interrupt wait state.
- `swi_add()`, `swi_sched()`, and `swi_remove()` implement software interrupt events and handler scheduling.
- Sysctls expose `hw.intrnames` and `hw.intrcnt`; DDB commands dump interrupt events and counts.

## Dependencies And Integration
Uses CK singly linked lists for handler lists, mutexes for event state, scheduler and thread locking, cpuset APIs, random entropy harvesting, NET_EPOCH, PMC hooks when enabled, machine interrupt/stat arrays, and DDB/debug infrastructure.

## Risk Notes
This is a high-risk synchronization file. Handler lists are traversed locklessly by `intr_event_handle()`, so removal relies on active phase counters and memory fences. Ithread state transitions depend on scheduler locks and atomic `it_need`/`ih_need` ordering. Affinity changes cross event locks, cpuset permission checks, and platform `assign_cpu` callbacks. Storm throttling and NET_EPOCH batching are performance-sensitive.
