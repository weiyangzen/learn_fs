# sources/test-tools/strace/bundled/linux/include/uapi/linux/mptcp.h

Purpose: defines Multipath TCP socket-level ABI for connection info, subflow information, full info queries, reset reasons, endpoint flags, and socket option numbers.

Important APIs/types/functions: key items include `MPTCP_SUBFLOW_FLAG_*`, `MPTCP_INFO_FLAG_*`, PM group names, endpoint/event flags, `struct mptcp_info`, reset reason constants, `mptcp_subflow_data`, `mptcp_subflow_addrs`, `mptcp_subflow_info`, `mptcp_full_info`, and socket options `MPTCP_INFO`, `MPTCP_TCPINFO`, `MPTCP_SUBFLOW_ADDRS`, `MPTCP_FULL_INFO`.

Control flow: applications call `getsockopt` on MPTCP sockets to retrieve aggregate connection state, TCP info arrays, subflow addresses, and combined full information. The kernel fills counts and size fields to support ABI growth.

State/persistence behavior: mostly observational; values reflect live MPTCP connection/subflow state, counters, tokens, and limits. Endpoint flags are shared with path manager netlink state.

Dependencies/integration: includes libc and Linux socket/in headers plus `mptcp_pm.h`. Integrates with TCP sockets, MPTCP path manager events, and netlink endpoint management.

Risks and test signals: variable array pointers and user/kernel size negotiation are key risks. Tests should cover all socket options, fallback/remote-key flags, reset reasons, subflow flag combinations, and IPv4/IPv6 address unions.
