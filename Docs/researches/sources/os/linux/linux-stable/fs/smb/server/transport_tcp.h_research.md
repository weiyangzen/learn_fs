# File Research: sources/os/linux/linux-stable/fs/smb/server/transport_tcp.h

## Summary
Declares the ksmbd TCP transport management API.

## Main Responsibilities
- Expose interface configuration and lookup helpers.
- Expose transport free, TCP init, and TCP destroy lifecycle functions.

## Cross-File Interactions
Used by IPC startup configuration and server lifecycle code. Implemented by `transport_tcp.c`.

## Risks
Small header, but the opaque `struct interface` contract is used across transport setup code and must remain consistent with TCP internals.
