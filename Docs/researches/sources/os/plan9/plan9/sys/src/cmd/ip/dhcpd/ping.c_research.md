# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/dhcpd/ping.c

`ping.c` probes whether an IPv4 address is already in use before leasing it.

Key behavior:
- `icmpecho` returns 0 immediately for non-IPv4 addresses.
- Dials ICMP echo service for the target.
- Sends up to three echo requests with message `"dhcp probe"`.
- Uses short alarms to wait for replies.
- Validates echo reply type, sequence, and payload before reporting address is live.

Important dependencies:
- Uses `../icmp.h`, Plan 9 `dial`, alarms, and note handler.

Notable risks/quirks:
- TODO comment notes no IPv6 ping.
- Sequence is derived from pid and time, not random.
