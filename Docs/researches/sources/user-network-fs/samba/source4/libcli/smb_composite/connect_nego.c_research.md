<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/smb_composite/connect_nego.c -->
# sources/user-network-fs/samba/source4/libcli/smb_composite/connect_nego.c

Purpose: provides a lower-level async helper that connects a TCP/NetBIOS socket and runs SMB dialect negotiation, returning an `smbXcli_conn` without creating a session or tree.

Important APIs and types: `struct smb_connect_nego_state`, `smb_connect_nego_send`, `smb_connect_nego_recv`, `smb_connect_nego_connect_done`, and `smb_connect_nego_nego_done`. It integrates `smbcli_sock_connect_send`, `smbXcli_conn_create`, and `smbXcli_negprot_send` with `tevent_req`.

Control flow: `send` copies options, computes NBT calling/called names, and starts socket connection, optionally to a supplied destination address. On connect completion it builds SMB1 capability flags from client options, creates an `smbXcli_conn` around the donated socket transport, frees the old `smbcli_socket`, and sends negotiate using min/max protocol and credit settings. The final recv moves the connection to the caller.

State and persistence: state is owned by the tevent request; the only persisted output is the moved `smbXcli_conn`. Timeout is derived from `request_timeout * 1000`. The helper has no authentication state and no filesystem side effects.

Risks: capability construction must remain aligned with SMB1 option semantics, especially Unicode, NTSTATUS, SPNEGO, signing, and oplock support. A NULL `called.name` posts a failed request. Test signals include SMB1 and SMB2 dialect negotiation paths, direct-address connections, capability bit selection, timeout behavior, and recv ownership transfer.
<!-- END_FILE_RESEARCH: sources/user-network-fs/samba/source4/libcli/smb_composite/connect_nego.c -->
