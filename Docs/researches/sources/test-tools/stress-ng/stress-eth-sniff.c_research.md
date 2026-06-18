# sources/test-tools/stress-ng/stress-eth-sniff.c

Purpose: implements `eth-sniff`, a Linux raw-packet sniffing stressor that receives Ethernet frames and records traffic rates by common IPv4 and IPv6 protocol numbers.

Important APIs/types/functions: `stress_eth_sniff_supported()` enforces `CAP_NET_RAW`. `common_proto_t` and `common_proto[]` map protocol numbers to metric labels. `stress_eth_sniff_metrics()` emits per-protocol KB/sec metrics. `stress_eth_sniff()` owns raw socket creation, packet receive, protocol classification, and cleanup.

Control flow: the stressor allocates a 65534-byte packet buffer, sync-starts, creates `socket(AF_PACKET, SOCK_RAW, htons(ETH_P_ALL))`, then loops on `recvfrom()`. It ignores short frames, reads the IP version from byte 14, validates IPv4 header length, accumulates payload bytes by protocol byte for IPv4 and IPv6, and increments bogo operations per classified packet. At stop it closes the socket, emits metrics for nonzero common protocols, and unmaps the buffer.

State and persistence behavior: state is local metric arrays and an anonymous packet buffer. It does not transmit packets or persist files; it passively observes packets visible to the host namespace and permissions.

Dependencies and integration points: Linux-only path requiring ethernet/IP headers, `AF_PACKET`, `SOCK_RAW`, `ETH_P_ALL`, mmap helpers, capability helpers, and stress-ng metrics/state APIs. Unsupported builds register an unimplemented stressor with the same capability check.

Risks: requires elevated raw socket rights and may expose traffic metadata in metrics. Packet parsing assumes Ethernet II layout without VLAN offset handling, so some frames are ignored or misclassified. Idle interfaces can produce few or no operations.

Test signals: run with and without `CAP_NET_RAW`, on active and quiet interfaces, confirm skip behavior on missing privileges, nonzero bogo count when traffic exists, and protocol metrics for TCP/UDP/ICMP where traffic is present.
