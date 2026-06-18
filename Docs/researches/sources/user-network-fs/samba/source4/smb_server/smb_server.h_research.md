# sources/user-network-fs/samba/source4/smb_server/smb_server.h

## Purpose
This header defines the shared source4 SMB server object model for connections, sessions, tree connects, handles, SMB1 requests, and common request/NTVFS macros. It is the central structure contract consumed by both SMB1 and SMB2 server code.

## Important APIs, Types, And Functions
Important types include `smbsrv_tcons_context`, `smbsrv_sessions_context`, `smbsrv_handles_context`, `smbsrv_session`, `smbsrv_tcon`, `smbsrv_handle`, `smbsrv_request`, and `smbsrv_connection`. It declares `smbsrv_add_socket` and includes generated prototypes. Macros include `SMBSRV_CHECK_WCT`, `SMBSRV_TALLOC_IO_PTR`, `SMBSRV_SETUP_NTVFS_REQUEST`, file-handle checks, `SMBSRV_CHECK`, `SMBSRV_CALL_NTVFS_BACKEND`, async status checks, and `SMBSRV_VWV_RESERVED`.

## Control Flow
The header itself has no runtime flow, but its macros define much of the SMB1 adapter flow: allocate typed IO, create an NTVFS request with session info and PID, attach frontend private data, dispatch synchronously or queue for async completion, and convert errors into SMB replies. Its structures determine how protocol handlers find sessions, tcons, handles, pending requests, signing context, packet state, share context, and negotiated parameters.

## State And Persistence
The defined structures hold all per-connection state: negotiated protocol/options, sessions, SMB1 tcons, SMB2 session-owned tcons, pending SMB1/SMB2 requests, signing contexts, partial transaction requests, statistics, share/loadparm pointers, SMB2 signing requirement, and highest SMB2 sequence number. Persistence beyond process memory is delegated to NTVFS/share/auth layers.

## Dependencies And Integration Points
The header depends on raw request/interface definitions, sockets, roles, dlink lists, NBT NDR, NTVFS forward declarations, and generated SMB server prototypes. It is included by SMB1, SMB2, session, tcon, handle, management, and service code.

## Risks And Test Signals
Risks include tight coupling through mutable structs, macro early returns, SMB1/SMB2 semantic differences in shared fields, id-tree limits, handle lifetime across session/tcon cleanup, and signing state consistency. Tests should stress connection teardown, multiple sessions, multiple tcons, handle enumeration/removal, SMB1 async operations, SMB2 pending request cleanup, and management/statistics visibility.
