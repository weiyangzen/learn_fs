# File Research: sources/os/bsd/openbsd-src/sys/sys/ipc.h

This header defines System V IPC permission structures and common constants.

Key definitions:
- `struct ipc_perm` with creator/current uid/gid, mode, sequence, and key.
- Permission bits: `IPC_R`, `IPC_W`, `IPC_M`.
- Creation/control flags: `IPC_CREAT`, `IPC_EXCL`, `IPC_NOWAIT`, `IPC_PRIVATE`.
- Control commands: `IPC_RMID`, `IPC_SET`, `IPC_STAT`.

Kernel APIs/macros:
- ID encoding helpers: `IPCID_TO_IX`, `IPCID_TO_SEQ`, `IXSEQ_TO_IPCID`.
- `ipcperm`

Userland declaration:
- `ftok`

Risk notes:
- IPC identifiers combine index and sequence into a single id; sequence rollover behavior matters for stale-id detection.
- `ipcperm` is the shared permission gate for msg/sem/shm style objects.
