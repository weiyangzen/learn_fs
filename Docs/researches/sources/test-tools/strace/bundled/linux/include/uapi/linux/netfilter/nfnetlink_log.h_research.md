# sources/test-tools/strace/bundled/linux/include/uapi/linux/netfilter/nfnetlink_log.h

Purpose: defines NFLOG nfnetlink ABI for packet log delivery and logging instance configuration.

Important APIs/types/functions: exports message types `NFULNL_MSG_PACKET` and `CONFIG`, packet header/hardware/timestamp structs, VLAN attrs, packet attrs for marks, ifindexes, hwaddr, payload, prefix, UID/GID, sequence numbers, conntrack info, VLAN and L2 headers, config command/mode structs, config attrs, copy modes, and config flags.

Control flow: userspace binds/unbinds logging groups, configures copy mode/range, buffer size, timeout, queue threshold, and flags, then receives logged packet messages containing selected metadata and payload.

State/persistence behavior: configuration messages mutate logging-instance state. Packet messages are transient; sequence counters and queueing behavior evolve with traffic.

Dependencies/integration: includes Linux types and `nfnetlink.h`; integrates with iptables/nftables log targets/expressions, conntrack metadata, and netlink multicast delivery.

Risks and test signals: packed config structs, endian timestamps, and optional metadata attrs require careful formatting. Tests should decode config commands/modes, copy modes, seq flags, conntrack attrs, VLAN nesting, and packet payload truncation.
