# sources/user-network-fs/samba/source4/libcli/raw/clitree.c

Purpose: manages SMB tree contexts, tree connect/disconnect, and a convenience full tree connection flow.

Important APIs: `smbcli_tree_init()`, `smb_raw_tcon_send()`, `smb_raw_tcon_recv()`, `smb_raw_tcon()`, `smb_tree_disconnect()`, and `smbcli_tree_full_connection()`.

Control flow: tree init steals or references a session and creates an SMBX tree connection object. TCON send supports old `SMBtcon` and `SMBtconX` levels, packing service/path/password/device. Recv validates the response, extracts TID, optional options/access masks, and device/filesystem strings. Disconnect sends `SMBtdis` and waits opportunistically. Full connection fills `smb_composite_connect` inputs and delegates to `smb_composite_connect()` to establish socket, session, and tree.

State and persistence: tree stores a session reference and SMBX tcon object. Remote tree connect/disconnect changes server-side share connection state.

Dependencies and integration: depends on raw request helpers, SMB composite connect, SMBX tcon creation, credentials/loadparm/resolver/event contexts, and client options.

Risks: SMB2 tree connect level is unsupported here. TCONX path is uppercased, which can matter for unusual servers. `smb_tree_disconnect()` returns the request destroy status even if receive was skipped or failed. Test signals include old TCON and TCONX parsing, optional access-mask fields, service/device string extraction, full connection with credentials, disconnect on null tree, and unsupported SMB2 level behavior.
