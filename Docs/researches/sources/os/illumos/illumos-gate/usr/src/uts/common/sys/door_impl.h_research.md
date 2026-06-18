# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/door_impl.h

## Scope

Complete file read, 49 lines. This small header holds common door implementation definitions shared by `sys/door.h` and `sys/proc.h`.

## Public Surface

It includes `sys/condvar.h` and defines:

- `door_pool_t`: a list of server threads plus a condition variable.

## Behavior And Integration

`door_pool_t` is embedded in door-related kernel structures to manage private or process-associated door server thread pools.

## Dependencies And Invariants

The `dp_threads` member points to `_kthread` objects, and `dp_cv` coordinates waiters on pool changes.

## Risks

This type is intentionally minimal and shared across core process and door headers. Changes affect both door IPC and process structures.
