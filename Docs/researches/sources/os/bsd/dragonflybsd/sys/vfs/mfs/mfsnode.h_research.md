# File Research: sources/os/bsd/dragonflybsd/sys/vfs/mfs/mfsnode.h

## Scope

Defines the in-memory control structure for MFS devices.

## Data Structures

- `struct mfsnode` stores backing memory base, filesystem size, service thread, bio request queue, synthetic device, active flag, and spare storage.
- Declares malloc type `M_MFSNODE` when malloc declarations are enabled.

## Dependencies

Requires kernel types for `caddr_t`, `struct thread`, `struct bio_queue_head`, and `cdev_t`.

## Risks And Invariants

`mfs_baseoff` and `mfs_size` define the trusted bounds for copyin/copyout I/O. `mfs_active` and `bio_queue` coordinate shutdown and service-loop wakeups.
