# sources/test-tools/stress-ng/stress-rawpkt.c research

Purpose: implements `rawpkt`, a Linux network stressor that sends and receives crafted Ethernet/IP/UDP frames over AF_PACKET raw sockets on loopback.

Important APIs, types, and functions: `stress_rawpkt_supported()` requires `CAP_NET_RAW`. `stress_rawpkt_sockopts()` exercises numerous `SOL_PACKET` getsockopt/setsockopt controls. `stress_rawpkt_client()` builds Ethernet, IPv4, and UDP headers and sends frames with `sendto()`. `stress_rawpkt_server()` receives AF_PACKET frames, filters for the expected loopback address/protocol/source port, optionally configures `PACKET_RX_RING` with TPACKET_V3, and records metrics.

Control flow: `stress_rawpkt()` reserves a per-instance port, queries loopback hardware address, IPv4 address, and interface index through `ioctl`, synchronizes, forks a client pinned near the parent CPU, and runs the server in the parent. The server loops receiving packets and increments bogo ops for matching UDP frames; the child loops sending incrementing IP IDs until stress stop. Parent kills/reaps the child at the end.

State and persistence: transient sockets, reserved port bookkeeping, and optional packet ring kernel buffers are used. No files persist.

Dependencies and integration: Linux packet sockets, UDP/IP headers, net ifreq ioctls, raw network capability, stress-ng network port reservation, affinity, signal, and checksum helpers. Classified as network and OS.

Risks: raw sockets require capabilities and may be blocked by container policy. Header fields must be byte-order correct; packet ring sizing requires a power-of-two option. Some sockopt calls intentionally use suspicious constants to exercise error paths and should ignore failures.

Test signals: capability skip, port reservation skip, loopback ioctl failures, receive MB/sec and packet metrics, bogo packet matches, and clean child termination.
