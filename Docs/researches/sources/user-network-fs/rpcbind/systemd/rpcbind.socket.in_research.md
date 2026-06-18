<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/rpcbind/systemd/rpcbind.socket.in -->
# sources/user-network-fs/rpcbind/systemd/rpcbind.socket.in

Purpose: Template version of the rpcbind systemd socket unit, adding conditional support for an abstract unix socket while otherwise matching the concrete socket unit.

Important directives: Same as `rpcbind.socket`, with `@ABSTRACT_TRUE@ListenStream=@/run/rpcbind.sock` allowing configure-time inclusion of the abstract socket. It sets `BindIPv6Only=ipv6-only` and binds stream/datagram sockets on IPv4 and IPv6 port 111.

Control flow and integration: Generated unit must align with daemon socket matching in `rpcbind.c`. Abstract socket support also aligns with `rpcinfo.c` local probing when `_PATH_RPCBINDSOCK_ABSTRACT` is defined.

State and persistence: No persistent state; generated content depends on configure substitution.

Risks: Incorrect `@ABSTRACT_TRUE@` substitution can leave invalid unit syntax or omit expected abstract socket support. Like the concrete unit, wildcard port 111 exposure depends on daemon policy and firewalling.

Test signals: Verify both generated variants, with and without abstract socket support. Confirm `rpcinfo` can connect via local socket and that daemon startup does not warn about dual-stack IPv6 sockets.
<!-- END_FILE_RESEARCH: sources/user-network-fs/rpcbind/systemd/rpcbind.socket.in -->
