# sources/user-network-fs/nfs-utils/support/nsm/rpc.c

Purpose: `rpc.c` constructs and parses the UDP ONC RPC messages statd needs without relying on a separate RPC client handle per program/version.

Important APIs and control flow: `nsm_next_xid`, `nsm_init_rpc_header`, and `nsm_init_xdrmem` prepare AUTH_NULL RPC messages. `nsm_xmit_getport` sends PMAP v2 queries for IPv4, `nsm_xmit_getaddr` sends RPCB v3 `GETADDR` for IPv6 when libtirpc is available, and `nsm_xmit_rpcbind` selects by address family. `nsm_xmit_notify` sends `SM_NOTIFY`; `nsm_xmit_nlmcall` sends the NLM callback requested by monitor records. Reply parsing is split into `nsm_parse_reply`, `nsm_recv_getport`, `nsm_recv_getaddr`, and `nsm_recv_rpcbind`.

State, dependencies, and integration: Static XID state is process-local. It uses XDR memory streams, rpcbind/pmap protocol definitions, `nfs_sockaddr2universal`, `nfs_universal2port`, and statd scheduling code.

Risks and test signals: XIDs are predictable and not synchronized across threads, only UDP is supported, PMAP is IPv4-only, and sendto short writes fail the call. Tests should cover XDR encode/decode, IPv4/IPv6 rpcbind, bad replies, unregistered programs, and malformed universal addresses.
