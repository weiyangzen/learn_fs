# File Research: sources/os/plan9/9front/sys/src/9/port/netif.h

Shared structures and constants for generic network interface devices.

Key contents:
- Defines Qid types and macros `NETTYPE`, `NETID`, and `NETQID`.
- Defines `Netfile` per-conversation state: owner, mode, type, flags, multicast bitmask, and input queue.
- Defines `Netaddr` multicast address entries.
- Defines `Netif` with conversation array, address/link fields, statistics, multicast state, and hardware callbacks.
- Declares generic netif operations.
- Defines Ethernet constants and `Etherpkt`.

Role:
- Provides the common shape used by Ethernet-like drivers to expose Plan 9 network files.

Notable constraints:
- Address size is capped at `Nmaxaddr = 64`.
- Multicast hash size is fixed at 31.
