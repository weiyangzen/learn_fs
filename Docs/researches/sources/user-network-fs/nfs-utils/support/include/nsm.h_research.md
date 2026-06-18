# sources/user-network-fs/nfs-utils/support/include/nsm.h

## Purpose
Declares Network Status Monitor support for rpc.statd state files, monitor/notify lists, and NSM RPC packet helpers.

## Important APIs, Types, and Functions
Defines `nsm_populate_t`, path/state/list management APIs, host insert/delete helpers, private-data hex conversion, NSM transmit/receive functions, and `NSM_MAXMSGSIZE`.

## Control Flow
Statd setup initializes pathnames and privileges, loads monitor/notify lists through callbacks, updates kernel state, and uses XDR helpers to send/parse rpcbind, notify, and NLM call messages.

## State and Persistence Behavior
Persistent state is statd monitor/notify directories and kernel NSM state. RPC functions operate on sockets and XDR streams.

## Dependencies and Integration Points
Depends on sockets, netdb, time, `sm_inter.h`, and RPC/XDR types. Integrated by rpc.statd file and RPC implementations.

## Risks and Edge Cases
State file migration, privilege dropping, IPv4/IPv6 rpcbind differences, and XDR bounds are key risks.

## Test Signals
Test state path setup, monitor insertion/deletion, notify list loading, private hex conversion, rpcbind getport/getaddr parsing, and malformed XDR replies.
