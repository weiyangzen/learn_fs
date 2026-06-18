# File Research: sources/os/linux/linux/fs/smb/server/transport_ipc.h

Declares the ksmbd IPC request API and lifecycle hooks.

Key contents:
- `KSMBD_IPC_MAX_PAYLOAD` fixed at 4096 bytes.
- Login, extended-login, tree connect, tree disconnect, logout, share config, SPNEGO authentication, and RPC command APIs.
- IPC handle allocation/free helpers.
- IPC release, soft reset, and init lifecycle functions.

Role in subsystem:
- Public kernel-internal interface for code that needs user-space daemon decisions or named-pipe/RPC mediation.
