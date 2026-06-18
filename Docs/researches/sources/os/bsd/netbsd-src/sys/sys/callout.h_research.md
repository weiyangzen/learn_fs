# File Research: sources/os/bsd/netbsd-src/sys/sys/callout.h

## Scope

Defines the public callout timer storage ABI and kernel callout APIs.

## APIs And Data Structures

- Public `callout_t` is opaque fixed-size storage of ten pointer slots.
- Defines internal flags `CALLOUT_BOUND`, `PENDING`, `FIRED`, `INVOKING` and user flag `CALLOUT_MPSAFE`.
- Private implementation defines circular queue linkage and `callout_impl_t` with callback, argument, CPU, time, flags, and magic.
- Kernel APIs cover startup, per-CPU init, hardclock processing, init/destroy, set function, reset/schedule, stop/halt, state queries, ack, and CPU binding.

## Dependencies

- Includes `sys/types.h`.

## Risks And Invariants

- `callout_t` must not grow for kernel module ABI compatibility.
- Private structure must fit inside caller-supplied opaque storage.
- MPSAFE flag affects kernel lock expectations for callback execution.
