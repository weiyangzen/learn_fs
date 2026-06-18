# File Research: sources/os/illumos/illumos-gate/usr/src/uts/common/sys/ipc.h

This public header defines common System V IPC permission and command constants.

Key definitions:
- `struct ipc_perm` includes owner/creator UID/GID, mode, sequence number, key, and ILP32 padding.
- Mode bits: `IPC_ALLOC`, `IPC_CREAT`, `IPC_EXCL`, `IPC_NOWAIT`.
- Key constant: `IPC_PRIVATE`.
- Control commands: `IPC_RMID`, `IPC_SET`, `IPC_STAT`.
- Declares `ftok(const char *, int)` under namespace conditions.

Dependencies:
- Includes `sys/isa_defs.h`, `sys/feature_tests.h`, and `sys/types.h`.

Relevance:
- General OS IPC ABI. Filesystem tools and daemons may use IPC, but this is not filesystem-specific.
