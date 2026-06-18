# File Research: sources/os/bsd/netbsd-src/sys/sys/mqueue.h

## Purpose
Defines POSIX message queue limits, attributes, and NetBSD kernel-side message queue state.

## Main API
- Public constants: `MQ_OPEN_MAX`, `MQ_PRIO_MAX`.
- Public structure: `struct mq_attr`.
- Kernel-only flags: `MQ_UNLINKED`, `MQ_RECEIVE`.
- Kernel constants: `MQ_NAMELEN`, `MQ_DEF_MSGSIZE`, `MQ_PQSIZE`, `MQ_PQRESQ`.
- Kernel structures: `mqueue_t`, `mq_msg_t`.
- Kernel functions: `mq_send1`, `mq_recv1`, `mqueue_get`, `mq_handle_open`, `mqueue_print_list`.

## Dependencies
Kernel mode depends on condition variables, mutexes, queues, select state, basic types, and `KERNEL_NAME_MAX` from `sys/param.h`.

## Risks and Notes
The implementation uses per-priority tail queues plus a bitmap, so priority bounds are part of the storage layout. Internal flags live in `mq_flags`, which POSIX permits, but consumers must not assume `mq_flags` contains only user-visible queue mode bits.
