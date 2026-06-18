# File Research: sources/os/bsd/freebsd-src/sys/sys/ipc.h

System V IPC common header defining `key_t`, `uid_t`, `gid_t`, `mode_t` exposure, `struct ipc_perm`, permission bits, creation flags, control commands, and `IPC_PRIVATE`.

Compatibility builds define `struct ipc_perm_old` and conversion helpers. Internal macros convert between IPC ids, array indices, and sequence numbers: `IPCID_TO_IX`, `IPCID_TO_SEQ`, and `IXSEQ_TO_IPCID`.

Kernel declarations include `ipcperm()` and shared memory lifecycle hooks for fork, exit, and object info. Userland exposes `ftok()`.
