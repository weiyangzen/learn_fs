# File Research: sources/os/bsd/freebsd-src/sbin/ipf/ipfsync/ipfsyncd.c

`ipfsyncd.c` is the daemon form of the IPFilter sync bridge. It relays synchronization records between the kernel sync device (`IPSYNC_NAME`) and a UDP peer or multicast group.

Major behaviors:
- Parses `-I interface`, `-i address`, `-p port`, and `-d` debug options.
- Defaults to UDP port `0xaf6c` and multicast group `INADDR_UNSPEC_GROUP | 0x697066`.
- Daemonizes when debug is disabled, installs termination handlers, and reconnects/reopens resources with exponential backoff.
- Builds sockets bound to a named interface, including multicast setup through IGMP raw socket, `IP_MULTICAST_IF`, `IP_MULTICAST_LOOP=0`, `IP_MULTICAST_TTL=63`, and `IP_ADD_MEMBERSHIP`.
- Uses `select()` to multiplex the kernel sync device and UDP socket.

Data handling:
- Kernel-to-network path reads buffered sync records, validates `SYNHDRMAGIC`, handles incomplete records with a retained buffer, and sends complete records over UDP.
- Network-to-kernel path receives UDP datagrams, validates sync headers, and writes complete records to `IPSYNC_NAME`.
- Debug helpers print sync header fields, command names (`SMC_CREATE`, `SMC_UPDATE`), table names (`SMC_NAT`, `SMC_STATE`), and TCP update state/age data.

Risks and quirks:
- Uses fixed 1400-byte buffers and manual record framing.
- Error recovery generally tears down fds and retries.
- `do_kbuff()` has fragile buffer accounting and copies leftover bytes manually.
