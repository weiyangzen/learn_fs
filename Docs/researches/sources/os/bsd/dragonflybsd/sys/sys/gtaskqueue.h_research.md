# File Research: sources/os/bsd/dragonflybsd/sys/sys/gtaskqueue.h

`gtaskqueue.h` is kernel-only and rejects userland inclusion. It defines group taskqueue structures and APIs, derived from FreeBSD taskqueue group support.

It defines task flags, `gtask_fn_t`, `struct gtask`, `struct grouptask`, group task name length, and helpers/macros for initialization and enqueueing. `grouptask` associates a generic task with a taskqueue, unique key, name, device, IRQ resource, and CPU binding.

The API covers queue block/unblock, cancel/drain, grouped enqueue, taskqgroup attach/detach/create/destroy/bind/drain, and SYSINIT-based `TASKQGROUP_DEFINE()`. It declares the `softirq` taskqgroup.
