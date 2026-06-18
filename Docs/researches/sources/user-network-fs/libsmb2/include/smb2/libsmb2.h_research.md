# sources/user-network-fs/libsmb2/include/smb2/libsmb2.h

## Purpose
`libsmb2.h` is the main public API header for libsmb2. It exposes context lifecycle, event-loop integration, authentication/session configuration, POSIX-like file/directory operations, share enumeration compatibility, UTF conversion helpers, compound PDU helpers, and server-side request handler interfaces.

## Important APIs, Types, and Functions
Important types include `struct smb2_context`, `struct smb2_iovec`, `smb2_command_cb`, `smb2_error_cb`, `struct smb2_stat_64`, `struct smb2_statvfs`, `struct smb2dirent`, `struct smb2_url`, opaque `struct smb2fh`/`struct smb2dir`, `enum smb2_negotiate_version`, `enum smb2_sec`, `struct smb2_server_request_handlers`, and `struct smb2_server`. Functions cover `smb2_init_context()`, close/destroy/active checks, fd/event callbacks, `smb2_service()`/`smb2_service_fd()`, timeout/passthrough/version/security/sign/seal/auth/user/password/domain/workstation setters, URL parsing, connect/disconnect, tree/session/PDU helpers, opendir/readdir/open/close/fsync/read/write/lseek/unlink/rmdir/mkdir/stat/statvfs/rename/truncate/readlink/echo/notify-change sync and async variants, UTF-8/UTF-16 conversion, and server bind/accept/serve.

## Control Flow
Client flow is: create a context, configure security/auth/user options, parse or provide server/share/path, connect asynchronously or synchronously, issue high-level or raw operations, drive async progress with fd readiness, then disconnect and destroy. Sync APIs wrap async operations with internal completion state. Server flow binds/listens, accepts connections into contexts, and dispatches decoded SMB2 commands to function pointers in `smb2_server_request_handlers`.

## State and Persistence Behavior
The context holds connection/session/tree/auth/crypto/queue state internally. File handles and directory handles are owned by the context and become invalid when the context is destroyed. Remote operations persist only when they modify the SMB share, such as write, unlink, mkdir, rename, truncate, and set-info-backed calls.

## Dependencies and Integration Points
It integrates with standard event loops via fd/event polling or callback registration, with Kerberos/NTLM authentication through configuration, with raw SMB2 structs from `smb2.h`, and with SRVSVC DCERPC share enumeration via the included compatibility header.

## Risks and Edge Cases
Async lifetime rules are central: callbacks can destroy contexts, PDUs can be cancelled by freeing them, and returned command data has command-specific ownership. `smb2_lseek(SEEK_END)` uses the original open EOF and does not refresh size. Some APIs require IPC$ or directory handles. Signing/sealing configuration must match server policy.

## Test Signals
Cover sync and async variants for connection, directory, file I/O, stat/statvfs, truncate, notify, and error cases. Test event-loop fd changes, Happy Eyeballs `smb2_get_fds()`, timeout servicing, context destruction from callbacks, server handler dispatch, and signing/encryption negotiation.
