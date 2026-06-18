# File Research: sources/os/bsd/freebsd-src/sys/sys/gtaskqueue.h

## Purpose
Declares kernel taskqueue group support for grouped tasks, dynamic thread groups, and IRQ/CPU binding.

## Main Interfaces
- Kernel-only header.
- `struct grouptask`: embedded `gtask`, taskqueue pointer, list linkage, unique key, name, device, IRQ resource, CPU.
- Queue APIs:
  - `gtaskqueue_block`
  - `gtaskqueue_unblock`
  - `gtaskqueue_cancel`
  - `gtaskqueue_drain`
  - `gtaskqueue_drain_all`
  - `grouptaskqueue_enqueue`
- Group task APIs:
  - `grouptask_block`
  - `grouptask_unblock`
  - `taskqgroup_attach`
  - `taskqgroup_attach_cpu`
  - `taskqgroup_detach`
  - `taskqgroup_create`
  - `taskqgroup_destroy`
  - `taskqgroup_bind`
  - `taskqgroup_drain_all`
- Initialization and enqueue macros: `GTASK_INIT`, `GROUPTASK_INIT`, `GROUPTASK_ENQUEUE`.
- Declaration/definition macros: `TASKQGROUP_DECLARE`, `TASKQGROUP_DEFINE`.
- Declares `qgroup_softirq`.

## Dependencies And Integration
Includes `_task.h`, bus/device types, taskqueue, and system types. `TASKQGROUP_DEFINE` uses SYSINIT ordering for creation and SMP binding.

## Risk Notes
Task group binding depends on init ordering (`SI_SUB_TASKQ`, `SI_SUB_SMP`). `GROUPTASK_NAMELEN` bounds task names at 32 bytes.
