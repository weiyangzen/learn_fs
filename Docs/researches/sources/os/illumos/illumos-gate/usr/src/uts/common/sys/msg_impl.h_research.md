# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/msg_impl.h

Kernel and compatibility implementation definitions for System V message queues.

Key responsibilities:
- Defines `msgsys()` subcommand numbers for get/control/receive/send/ids/snapshot.
- Defines wakeup records and selection callback chains used to decide which blocked sender/receiver to wake.
- Defines internal `struct msg` entries stored on queue lists, including type, size, message address, flags, and copyout reference count.
- Defines internal per-queue `kmsqid_t` state: permissions, message list, byte/count limits, PIDs/timestamps, sender/receiver wait counts, lowest type, wake selection lists, condition variables, and wait-list buckets.
- Defines condition-variable sharding constants for message receive wakeups.
- Defines ILP32 views of message buffers, snapshot headers, and `msqid_ds` for 32-bit syscall compatibility on LP64 kernels.

Dependencies:
- Includes `sys/ipc_impl.h`; kernel/kmem users include `sys/msg.h`, `sys/t_lock.h`, and `sys/list.h`.

Notable risks:
- Queue wakeup logic depends on multiple wait lists and per-message copyout flags; races can produce missed wakeups or use-after-free if invariants are broken.
- 32-bit compatibility structures must track the public ABI exactly.
