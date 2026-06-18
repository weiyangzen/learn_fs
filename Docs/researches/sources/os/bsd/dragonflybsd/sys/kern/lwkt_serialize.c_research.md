# File Research: sources/os/bsd/dragonflybsd/sys/kern/lwkt_serialize.c

## Scope

This file implements DragonFlyBSD's low-level LWKT serializer: a non-recursive exclusive interlock that may be held across blocking operations and has integrated interrupt-handler enable/disable support for driver code.

## Public And Internal APIs Covered

- Lifecycle and locking: `lwkt_serialize_init()`, `lwkt_serialize_enter()`, `lwkt_serialize_try()`, `lwkt_serialize_exit()`, `lwkt_serialize_adaptive_enter()`.
- Interrupt handler gating: `lwkt_serialize_handler_disable()`, `lwkt_serialize_handler_enable()`, `lwkt_serialize_handler_call()`, `lwkt_serialize_handler_try()`.
- Sleep/wakeup callbacks: internal `lwkt_serialize_sleep()` and `lwkt_serialize_wakeup()`.

## Control Flow And Behavior

- `lwkt_serialize_init()` initializes the atomic interrupt-aware interlock and sets `last_td` to a sentinel.
- `lwkt_serialize_enter()` asserts non-ownership, enters through `atomic_intr_cond_enter()`, and records `curthread`.
- `lwkt_serialize_try()` attempts nonblocking acquisition through `atomic_intr_cond_try()` and returns non-zero on success.
- `lwkt_serialize_exit()` asserts ownership, clears `last_td` to a sentinel, and releases via `atomic_intr_cond_exit()` with wakeup callback.
- Handler disable/enable use the interrupt-handler bit in the same interlock word.
- `lwkt_serialize_handler_call()` checks that the handler is enabled, acquires the serializer, rechecks enablement, invokes the handler if still enabled, then releases.
- `lwkt_serialize_handler_try()` provides the same handler wrapper without sleeping.
- `lwkt_serialize_sleep()` interlocks a sleep against missed wakeups by checking the atomic condition after `tsleep_interlock()`.
- `lwkt_serialize_adaptive_enter()` first tries immediate acquisition, spins for `SLZ_ADAPTIVE_SPINMAX`, then increments sleeper state and sleeps, restarting after wake.

## State And Data Structures

- `lwkt_serialize` contains an `atomic_intr` interlock and `last_td` debug/ownership tracking field.
- KTR events trace enter, exit, sleep, wakeup, try, and adaptive-spin stages.

## Dependencies

- Depends on machine atomic interrupt-condition primitives, `tsleep`, `wakeup`, critical interlocks, and assertion macros from `sys/serialize.h`.
- Used by drivers and message-port serializer backends where interrupt handlers and thread context must be mutually excluded.

## Risks And Invariants

- Serializers are explicitly non-recursive; callers must not enter while already serialized.
- Handler wrappers must recheck handler enablement after acquiring the serializer to close disable races.
- Sleep path must avoid lost wakeups between contention detection and actual sleep.
- This is not a mutex; it is a lower-level primitive with different ownership and interrupt semantics.
