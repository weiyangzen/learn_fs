# File Research: sources/os/linux/linux-stable/fs/smb/server/ksmbd_netlink.h

Read status: complete.

## Purpose
Defines the packed generic-netlink ABI between the kernel ksmbd server and its userspace IPC daemon.

## Main Contents
- Generic netlink name/version and maximum account/hash/share-name sizes.
- Startup, shutdown, heartbeat, login, login-extension, share-config, tree-connect, tree-disconnect, logout, RPC, and SPNEGO auth request/response structs.
- Payload helper macros/functions for variable-length interface, veto-list, share-path, RPC, and SPNEGO data.
- Event enum with request/response pairing assumptions.
- User, share, tree-connect, RPC, and config option flags/status constants.

## Dependencies And Role
This is a userspace ABI consumed by transport IPC and ksmbd-tools. It supplies account database, share configuration, tree authorization, RPC offload, and Kerberos/SPNEGO data to kernel code.

## Risks
ABI layout is packed and externally visible. Field size, enum value, flag, or payload-layout changes require userspace coordination and backward-compatibility care.
