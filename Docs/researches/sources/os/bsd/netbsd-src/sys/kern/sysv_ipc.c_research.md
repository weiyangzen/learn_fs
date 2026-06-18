# File Research: sources/os/bsd/netbsd-src/sys/kern/sysv_ipc.c

Read completely: 523 lines.

Implements NetBSD's shared System V IPC module glue: module initialization/finalization, dynamic syscall registration, common IPC permission checks through kauth, and the `kern.ipc.sysvipc_info` sysctl that reports message queue, semaphore, and shared memory configuration/state.

Compile-time configuration:
- Includes `opt_sysv.h`, `opt_sysvparam.h`, and `opt_compat_netbsd.h` under `_KERNEL_OPT`.
- Builds feature sections only when `SYSVSHM`, `SYSVSEM`, and/or `SYSVMSG` are defined.
- Provides global default tunables/limits: `struct shminfo shminfo`, `struct seminfo seminfo`, and `struct msginfo msginfo`, conditionally compiled for the enabled components.

Module/syscall registration:
- Declares `MODULE(MODULE_CLASS_EXEC, sysv_ipc, NULL)`.
- `sysvipc_syscalls[]` lists the syscall package entries to establish for enabled SysV IPC components:
  - shared memory: `SYS___shmctl50`, `SYS_shmat`, `SYS_shmdt`, `SYS_shmget`
  - semaphores: `SYS_____semctl50`, `SYS_semget`, `SYS_semop`, `SYS_semconfig`, `SYS_semtimedop`
  - message queues: `SYS___msgctl50`, `SYS_msgget`, `SYS_msgsnd`, `SYS_msgrcv`
- `sysv_ipc_modcmd()` handles `MODULE_CMD_INIT` by installing the kauth listener, establishing syscall entries, and initializing enabled subcomponents in shared-memory, semaphore, then message-queue order.
- `MODULE_CMD_FINI` finalizes enabled subcomponents in the same dependency-aware sequence, refuses unload with `EBUSY` when a subcomponent is active, reinitializes already-finalized earlier components if a later component blocks unload, disestablishes syscalls, and removes the kauth listener.
- Unknown module commands return `ENOTTY`.

Permission model:
- A single `sysvipc_listener` is registered on `KAUTH_SCOPE_SYSTEM`.
- `sysvipc_listener_cb()` handles only `KAUTH_SYSTEM_SYSVIPC` with `KAUTH_REQ_SYSTEM_SYSVIPC_BYPASS`; unrelated authorization requests defer.
- For `IPC_M`, only owner or creator effective UID matches allow access; otherwise it defers, leading to `EPERM`.
- For read/write requests, it maps `IPC_R` and `IPC_W` to owner/group/other mode bits in `struct ipc_perm`, checking effective UID, creator UID, group membership in `gid` or `cgid`, then other permissions.
- `ipcperm()` wraps `kauth_authorize_system()` and maps non-`IPC_M` denial to `EACCES`, preserving the traditional distinction between modification ownership failures and access-mode failures.

SysV IPC sysctl:
- `sysctl_ipc_setup` creates the permanent `kern.ipc` node and `kern.ipc.sysvipc_info` struct sysctl.
- `sysctl_kern_sysvipc()` first calls the compatibility hook `sysvipc_sysctl_50_hook`; if the hook handles the request, its result is returned, otherwise native handling continues after `EPASSTHROUGH`.
- Accepts exactly one selector under the sysctl: `KERN_SYSVIPC_MSG_INFO`, `KERN_SYSVIPC_SEM_INFO`, or `KERN_SYSVIPC_SHM_INFO`, returning `EINVAL` if the requested component is not compiled in.
- Computes the info header size plus an array of per-object descriptors, rounds the header to a 64-bit boundary when needed, supports size-query calls with `oldp == NULL`, allocates a zeroed temporary buffer with `kmem_zalloc`, fills the global info structure, then optionally fills each object descriptor.
- Message queue descriptor filling is protected by `msgmutex`; semaphore and shared-memory descriptors are filled through `SYSCTL_FILL_SEM` and `SYSCTL_FILL_SHM`.
- Uses `copyout()` to return the bounded buffer to user space and frees it with `kmem_free()`.

Concurrency and integration:
- Integrates with kernel modules, dynamic syscall establishment, kauth, sysctl, compatibility module hooks, component-specific SysV IPC implementations, and kernel memory allocation.
- The kauth listener lifetime is guarded by `KASSERT` checks in `sysvipcinit()` and `sysvipcfini()`.
- Module unload depends on component-specific `shmfini()`, `semfini()`, and `msgfini()` busy checks.

Risks and notes:
- `MODULE_CMD_INIT` does not undo `syscall_establish()` or `sysvipcinit()` if a later subcomponent initializer fails; it only unwinds already-initialized SysV subcomponents.
- The sysctl copies a snapshot assembled in a temporary buffer; message queues are individually mutex-protected while copied, but semaphore/shared-memory consistency depends on their fill macros and backing synchronization.
- The sysctl returns `ENOMEM` both when the caller's buffer cannot hold the info header and when it truncates during descriptor filling; on successful `copyout`, the earlier truncation status is preserved.
- Component availability and syscall/sysctl surface are compile-time dependent, so kernels built with only part of SysV IPC expose only that subset.
