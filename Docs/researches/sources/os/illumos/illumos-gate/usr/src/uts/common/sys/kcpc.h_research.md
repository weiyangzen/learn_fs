# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/kcpc.h

## Role

`kcpc.h` defines the kernel-facing CPU performance counter (CPC) programming interface. It exposes the opaque `kcpc_set_t` type to all consumers and, under `_KERNEL`, the set/request structures and functions used to bind, program, sample, list, and manage hardware performance counter events.

## Major Definitions

Inside the kernel, `struct _kcpc_set` holds set flags, request count, request array, data storage, owning CPC context, bound/unbound state, mutex, and condition variable. `KCPC_SET_BOUND` marks bound state. `struct _kcpc_request` stores PCBE-specific configuration, data index, physical PIC number, context PIC pointer, data pointer, event name, preset value, flags, attributes, and a caller-owned pointer. `kcpc_request_list_t` is a dynamically managed list of counter-event requests.

Function pointer types describe a per-counter update callback and a current-CPU read function.

## Interfaces

The kernel API includes framework initialization, thread/CPU binding, sampling into user buffers with time/tick data, CPU context creation, event support checks, request-list init/add/reset/free, current-CPU read/program/unprogram operations, unbind, preset, restart, enable/disable, thread-context invalidation, overflow handling, CPU/LWP hooks, idle context installation, CPU context freeing, config iteration/invalidation/freeing, event/attribute listing, PCBE capability/loading checks, nonprivileged access checks, and PCBE registration.

It also declares global CPC CPU-context lock/count state and DTrace CPC integration globals: `dtrace_cpc_in_use` and `dtrace_cpc_fire`.

## Integration Notes

This header sits between kernel CPC consumers, DTrace, CPU context switching, and processor-specific back-end engines. Locking and state transitions are part of the exported structure contract for kernel code. Because counters can be bound to threads or CPUs and can overflow asynchronously, callers must coordinate lifecycle, invalidation, and context programming carefully.
