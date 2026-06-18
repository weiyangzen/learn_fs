# sources/user-network-fs/samba/source3/libsmb/smbsock_connect.h

Purpose: `smbsock_connect.h` declares the SMB transport connection API implemented by `smbsock_connect.c`. It separates socket/transport establishment from higher-level SMB session negotiation.

Important APIs and types: it forward-declares `struct smbXcli_transport` and declares `smbsock_transports_from_port`, the `smbsock_connect_require_bsd_socket` policy flag, one-address async/sync connection functions, and multi-address async/sync connection functions. The async APIs return `struct tevent_req *`; recv APIs move an `smbXcli_transport` into caller memory. `smbsock_any_connect_recv` can also return the selected address index.

Control flow and state: callers pass a `tevent_context`, `loadparm_context`, sockaddr(s), transport list, optional called/calling NetBIOS names and types, and talloc output context. The implementation owns transient sockets and returns one transport on success. The `NONNULL` annotations document required inputs.

Dependencies and integration: the header depends on Samba transport types, NTSTATUS, tevent, talloc, loadparm, and socket address structures through included/consumer context. It is used by client connection code that wants configured SMB transports, including TCP/NBT/QUIC when available.

Risks: the global `smbsock_connect_require_bsd_socket` changes behavior process-wide, so users must set it deliberately. Passing a transport list inconsistent with the address/target name can yield `NT_STATUS_PORT_NOT_SET` or skip QUIC.

Test signals: compile tests should validate async and sync prototypes. Integration tests should connect by single address and address list, verify chosen index, and exercise the global BSD socket policy in code paths that require it.
