# File Research: sources/os/bsd/dragonflybsd/sys/kern/sysv_ipc.c

## Summary
Implements the shared SysV IPC permission check helper `ipcperm()`.

## Main Responsibilities
- Compares caller credentials against IPC creator/owner UID and GID fields.
- Applies owner, group, or other permission bits by shifting the requested mode.
- Allows metadata-control requests (`IPC_M`) for privileged callers.
- Allows read/write style access when requested bits are present or the caller has restricted-root capability.

## Important Behavior
If the effective UID does not match creator or owner, group membership is checked against both current and creator group IDs; otherwise permission falls through to "other" bits. `IPC_M` bypasses normal mode matching for privileged callers. Non-control operations succeed when all requested bits are present in `perm->mode` or `caps_priv_check(..., SYSCAP_RESTRICTEDROOT)` succeeds.

## Dependencies and Integration
`ipcperm()` is shared by SysV message queues, semaphores, and shared memory. It depends on process credentials, group membership, and DragonFly capability checks.

## Risks
Permission semantics are central to all SysV IPC objects. Any change affects message queues, semaphores, and shared memory together, including jail/capability behavior enforced by callers.
