# sources/user-network-fs/samba/source4/libcli/libcli.h

Purpose: broad SMB client API header exposing the classic `smbcli_state` stack and many synchronous SMB1 helper functions.

Important types: `struct smbcli_state` groups options, socket, transport, session, tree, substitution context, and LSA state. `struct clilist_file_info` models directory list entries. `struct nbt_dc_name` contains DC address/name. `enum brl_type` defines byte-range lock kinds.

Important APIs: declares socket connect, negotiate, session setup, tree connect/disconnect, full connection, file read/write/open/close, UNIX extension operations, rename/delete/mkdir/rmdir, locking/unlocking, file attribute/query operations, directory listing, messaging, and delete-tree helpers.

Control flow contract: callers typically initialize state, connect socket/transport, negotiate, establish session, connect tree, then use file/tree operations. Many functions are synchronous wrappers around raw request implementations.

State and persistence: the header defines in-memory client state only. File operations affect remote SMB server state; no local persistence is defined.

Dependencies and integration: includes generated NBT definitions and raw client headers. It is a central include for RAP and raw SMB client modules.

Risks: the API surface is large and SMB1-centric. Callers must respect tree/session/transport lifetime layering. Test signals include full connection setup, all state teardown paths, UNIX extension calls on capable/incapable servers, old/new directory listing variants, and locking semantics.
