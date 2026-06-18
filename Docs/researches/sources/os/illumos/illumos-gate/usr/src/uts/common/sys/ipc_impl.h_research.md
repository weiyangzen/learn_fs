# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ipc_impl.h

This private header defines kernel and cross-data-model implementation details for System V IPC.

Public/cross-model structures:
- `ipc_time_t` is `uint64_t`.
- 64-bit control commands: `IPC_SET64`, `IPC_STAT64`.
- Under `_SYSCALL32`, `struct ipc_perm32` mirrors 32-bit userland layout.
- `ipc_perm64_t` is a stable user/kernel layout for 64-bit IPC control structures.
- `struct shmid_ds64`, `struct semid_ds64`, and `struct msqid_ds64` provide model-independent shared memory, semaphore, and message queue status layouts.

Kernel internals:
- ID encoding macros: sequence bits/mask/shift, index mask, `IPC_SEQ`, `IPC_INDEX`.
- Table sizing and invalid ID constants.
- Resource-control accounting macros: `IPC_PROJ_USAGE`, `IPC_ZONE_USAGE`.
- Lock assertion helper `IPC_LOCKED`.
- `kipc_perm_t` is the kernel IPC permission object with AVL/list links, refcount, credentials, project, IPC ID, zone ID, and zone ref.
- `ipc_slot_t` stores bucket lock, object pointer, sequence, stale-chain pointer, and padding.
- `ipc_service_t` stores global service state: lock, key tree, table, counts, rctl handles/offsets, ID space, object size/destructors, used-ID list, and audit type.

Kernel functions:
- Permission checks/stat/set, service create/destroy/lock/unlock, object lookup/hold/release/get/commit/cleanup/remove/list, and zone cleanup.

Userland fallback:
- When not `_KERNEL`, declares `msgctl64`, `semctl64`, and `shmctl64`.

Dependencies:
- Includes IPC, mutex, resource control, project, zone, sysmacros, AVL, ID space, credentials, and list headers.

Relevance:
- General kernel IPC infrastructure. Not filesystem-specific but important OS substrate.
