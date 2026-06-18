# File Research: sources/os/bsd/netbsd-src/sys/sys/ipc.h

Provides System V IPC permission and command definitions. `ipc_perm` stores owner/creator IDs, mode, private sequence, and key. NetBSD exposes `ipc_perm_sysctl` for sysctl reporting. It defines permission bits, creation flags, private key, control commands, IPC ID sequence/index helpers, and `ftok`.

In-kernel declarations include `ipcperm`, SysV IPC init/fini, sysctl fill helpers, and COMPAT_50 sysctl setup. ABI risks involve IPC ID encoding, sequence wrap behavior, and matching permission semantics across message queues, semaphores, and shared memory.
