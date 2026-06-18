# File Research: sources/os/bsd/freebsd-src/sys/kern/sysv_ipc.c

## Purpose

`sysv_ipc.c` provides shared System V IPC support code used by System V message queues, shared memory, and semaphores. In this group, its most important role is the common `ipcperm()` discretionary permission check used by `sysv_msg.c`.

## SYSVSHM Stub Hooks

When `SYSVSHM` is not compiled in, the file defines hook pointers and wrappers for shared-memory lifecycle integration:

- `shmfork_hook`
- `shmexit_hook`
- `shmobjinfo_hook`
- `shmfork(struct proc *p1, struct proc *p2)`
- `shmexit(struct vmspace *vm)`
- `shmobjinfo(struct vm_object *obj, key_t *key, unsigned short *seq)`

The wrappers call hooks when present. `shmobjinfo()` defaults `key` and `seq` to zero for absent `sysvshm.ko`.

## `ipcperm()`

`ipcperm(struct thread *td, struct ipc_perm *perm, int acc_mode)` implements common System V IPC permission checks.

Permission model:

- If the caller is the creator or current owner (`cuid` or `uid`), it uses owner mode bits and grants `IPC_M`.
- If the caller is in the creator/current group (`cgid` or `gid`), it uses group mode bits.
- Otherwise, it uses other mode bits.
- Read/write permissions are derived from `IPC_R` and `IPC_W`.
- Although System V IPC mode bits can represent `IPC_M`, this implementation requires privilege for administrative rights unless the caller is owner/creator.

Privilege fallback:

- Missing `IPC_M` can be satisfied by `PRIV_IPC_ADMIN`.
- Missing `IPC_R` can be satisfied by `PRIV_IPC_READ`.
- Missing `IPC_W` can be satisfied by `PRIV_IPC_WRITE`.
- If DAC plus privilege covers all requested bits, the function returns `0`; otherwise it returns `EACCES`.

The comment notes MAC Framework checks are intentionally not embedded in `ipcperm()`. MAC checks are performed at primitive-specific entry points, complementing these discretionary checks.

## Compatibility Conversions

For older FreeBSD compatibility builds, the file converts between old and current IPC permission layouts:

- `ipcperm_old2new()`
- `ipcperm_new2old()`

For 32-bit compatibility builds, it converts between 32-bit user-visible structures and native kernel structures:

- `freebsd32_ipcperm_old_in()`
- `freebsd32_ipcperm_old_out()`
- `freebsd32_ipcperm_in()`
- `freebsd32_ipcperm_out()`

These conversions use field-by-field copies for credential IDs, mode, sequence, and key fields.

## Research Notes

This file is small but security-sensitive. Its central contract is that System V IPC objects share one DAC permission implementation, while subsystem-specific files add MAC, jail, accounting, object lifecycle, and syscall semantics. Changes to `ipcperm()` affect all System V IPC primitives.
