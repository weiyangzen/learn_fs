# sources/user-network-fs/samba/source4/libcli/raw/clisocket.c

Purpose: asynchronous and synchronous creation of `smbcli_socket` connections to SMB servers by IP address or resolved NetBIOS name.

Important APIs: `smbcli_sock_connect_send()`, `smbcli_sock_connect_recv()`, and `smbcli_sock_connect()`. Internal helpers resolve names, submit multi-address SMB socket connection attempts, and receive the resulting transport.

Control flow: send creates composite state, copies options/socket names, duplicates calling/called NBT names, interprets numeric host addresses directly, or starts `resolve_name_send()` for host lookup. Resolved string addresses are converted to `sockaddr_storage`; `smbsock_any_connect_send()` tries the address set using configured transports and NetBIOS names. On success, it creates `smbcli_socket`, moves in the `smbXcli_transport`, stores hostname and event context, then completes the composite.

State and persistence: all connection attempt state is talloc-owned under the composite. Result socket owns the transport and hostname. No disk persistence.

Dependencies and integration: depends on composite helpers, resolver, Samba socket connect helpers from source3, NBT names, loadparm, and SMB raw socket structures.

Risks: failure paths often free the whole composite and return null, so callers must handle allocation/setup failures separately from asynchronous NTSTATUS errors. `socket_options` is referenced but not used directly in this file. Test signals include numeric IP, resolved multi-address host, bad resolved address, NBT name duplication failure, all transport fallback, and destructor freeing underlying transport.
