# File Research: sources/os/linux/linux-stable/fs/smb/server/transport_ipc.h

## Summary
Declares the ksmbd IPC API used by kernel server code to communicate with the user-space daemon.

## Main Responsibilities
- Define the maximum IPC payload size.
- Declare login, SPNEGO, share config, tree connect/disconnect, logout, IPC id, and RPC forwarding helpers.
- Declare IPC lifecycle functions for init, release, and soft reset.

## Cross-File Interactions
Used by management, authentication, tree connection, and named-pipe/RPC code. Implemented entirely by `transport_ipc.c`.

## Risks
Prototype and payload-size contract changes must remain synchronized with the netlink message formats shared with user-space ksmbd tools.
