# File Research: sources/os/bsd/dragonflybsd/sys/sys/ipc.h

`ipc.h` defines SVID/System V IPC common types, permission structure, constants, and helper macros. It includes `sys/cdefs.h` and `machine/stdint.h`, and conditionally typedefs `gid_t`, `key_t`, `mode_t`, and `uid_t`.

`struct ipc_perm` stores creator/current UID/GID, permission mode, sequence number, and user-specified key. Constants include BSD-visible read/write/control permission bits, `IPC_CREAT`, `IPC_EXCL`, `IPC_NOWAIT`, `IPC_PRIVATE`, and control operations `IPC_RMID`, `IPC_SET`, and `IPC_STAT`.

Kernel builds get ID/index/sequence conversion macros and `ipcperm()`. Userland gets the historical `ftok()` declaration.
