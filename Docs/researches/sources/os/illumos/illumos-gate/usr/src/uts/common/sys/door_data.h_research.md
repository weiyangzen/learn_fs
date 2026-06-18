# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/door_data.h

## Scope

Complete file read, 126 lines. This kernel-only header defines per-thread data used during door invocations.

## Public Surface

Under `_KERNEL`, it defines:

- `door_layout_t`: stack layout locations for descriptors, data, door info, results, and final stack pointer.
- `door_upcall_t`: credential and maximum reply data/descriptor limits for upcalls.
- `door_client_t`: per-client invocation args, upcall information, temporary buffer, file pointer array, error, condition variable, and state flags.
- `door_server_t`: caller thread, server list, active door, pool, saved layout/stack info, condition variable, and state flags.
- `door_data_t`: combined client/server per-thread data.
- `DOOR_CLIENT()` and `DOOR_SERVER()` accessors.
- Thread hold/release macros `DOOR_T_HELD`, `DOOR_T_HOLD`, and `DOOR_T_RELEASE`.
- `DOOR_ROUND` buffer-size rounding value.

## Behavior And Integration

Each door call affects client state on one thread and server state on another. This split allows a server thread to make nested door calls without clobbering its server-side invocation context.

## Dependencies And Invariants

The header depends on `sys/door.h`, `sys/thread.h`, and `sys/file.h` for kernel builds. Hold/release macros assert correct state and broadcast on release.

## Risks

This is private scheduler/IPC state. Incorrect hold/release pairing can leave threads stuck or allow stack/result teardown too early. Buffer rounding reduces overflow frequency but does not remove the need for result-size checks.
