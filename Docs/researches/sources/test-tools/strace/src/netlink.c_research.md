<!-- BEGIN_FILE_RESEARCH: sources/test-tools/strace/src/netlink.c -->
# sources/test-tools/strace/src/netlink.c

Purpose: central netlink message decoder for socket payloads, including `nlmsghdr` arrays, type/flag rendering, control messages, and dispatch into family-specific payload decoders.

Important APIs/types/functions: `decode_netlink`, `fetch_nlmsghdr`, `get_fd_nl_family`, `decode_nlmsg_type`, `decode_nlmsg_flags`, `decode_nlmsgerr`, `decode_payload`, `print_nlmsghdr`, `netlink_decoders`, and xlat tables for audit, crypto, generic, netfilter, route, SELinux, sock_diag, and xfrm families.

Control flow: `decode_netlink` infers the netlink family from fd inode/socket details, special-cases `NETLINK_KOBJECT_UEVENT`, iterates aligned `nlmsghdr` records with sequence truncation checks, prints each header, and passes payloads to reserved-control handling or family decoders. `NLMSG_ERROR` payloads are decoded as `struct nlmsgerr`, optionally followed by extended ack attributes.

State and persistence behavior: no durable state; it reads tracee memory and fd metadata. The only persisted information is external to this file, such as generic family mappings and tcb output/aux state.

Dependencies and integration points: integrates with `netlink.h`, `nlattr.h`, family decoders (`decode_netlink_crypto`, `decode_netlink_route`, etc.), fd inode/socket lookup helpers, `genl_families_xlat`, and many generated xlat tables.

Risks: fd-family inference depends on `/proc` socket detail strings and can fall back to generic decoding. Alignment, malformed `nlmsg_len`, capped errors, and family-specific flag tables are sensitive to kernel ABI changes.

Test signals: cover single and multi-message buffers, short headers, unknown families, `NLMSG_DONE`, `NLMSG_ERROR` with and without `NLM_F_CAPPED`, extended ack attributes, netfilter split types, and route/generic/sock_diag dispatch.
<!-- END_FILE_RESEARCH: sources/test-tools/strace/src/netlink.c -->
