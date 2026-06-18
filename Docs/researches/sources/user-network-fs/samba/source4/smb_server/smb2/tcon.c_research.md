# sources/user-network-fs/samba/source4/smb_server/smb2/tcon.c

## Purpose
This file implements SMB2 tree connect/disconnect, SMB2 wire-handle translation, NTVFS handle callbacks, and unsolicited oplock-break sending. It bridges SMB2 sessions and tree ids to Samba share configuration and NTVFS connections.

## Important APIs, Types, And Functions
Public functions are `smb2srv_pull_handle`, `smb2srv_push_handle`, `smb2srv_tcon_recv`, and `smb2srv_tdis_recv`. Key internal functions include `smb2srv_send_oplock_break`, handle callbacks `smb2srv_handle_create_new`, `smb2srv_handle_make_valid`, `smb2srv_handle_destroy`, wire-key stubs, `smb2srv_tcon_backend`, `smb2srv_tcon_send`, `smb2srv_tdis_backend`, and `smb2srv_tdis_send`.

## Control Flow
Tree connect decodes the UNC path, strips leading server components, looks up share config, applies hosts allow/deny, maps share type to NTVFS disk/print/IPC, allocates an SMB2 tcon under the session, initializes an NTVFS connection, registers oplock/address/handle callbacks, creates an NTVFS request, calls `ntvfs_connect`, and replies with share type, flags, capabilities, access mask, and TID. Handle push encodes HID/TID/VUID into SMB2’s 128-bit handle. Pull validates VUID, finds the referenced tcon by embedded TID, finds the handle, updates `req->tcon`, and returns the NTVFS handle. Tree disconnect frees the tcon after a success status.

## State And Persistence
This file creates and destroys session-owned tcons and handle front-end objects. It updates `req->tcon`, sets `handle->ntvfs` once backends make a handle valid, moves valid handles under the tcon memory context, and frees handle wrappers on destroy. Share/file persistence is through NTVFS.

## Dependencies And Integration Points
It depends on share configuration, socket access checks, NTVFS connection and callbacks, common tcon/handle allocation in `smb_server/tcon.c` and handle modules, packet send from `receive.c`, and SMB2 file operations that call `smb2srv_pull_handle`.

## Risks And Test Signals
Risks include incomplete durable handle wire-key callbacks, wildcard handle returning NULL, related/chained handle TODO semantics, share path parsing edge cases, tcon lifetime with open handles, and forcing broad `SEC_RIGHTS_FILE_ALL` access in replies. Tests should cover UNC path forms, hosts allow/deny, disk/IPC/printer shares, handle use through a different header TID, invalid VUID/TID/HID, oplock break emission, tree disconnect with open handles, and chained create/read/write.
