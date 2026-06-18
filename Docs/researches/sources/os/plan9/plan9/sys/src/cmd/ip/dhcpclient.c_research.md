# File Research: sources/os/plan9/plan9/sys/src/cmd/ip/dhcpclient.c

`dhcpclient.c` is a DHCPv4 client that prints acquired configuration and renews leases.

Key behavior:
- Usage: `dhcpclient [-x netextension]`.
- Maintains global `dhcp` state protected by `QLock`.
- Initializes xid from `/dev/random` or time/pid, constructs client id from `sysname.pid`.
- Opens UDP port 68 in header mode.
- Sends Discover, waits for Offer, sends Request, waits for Ack, then prints `ip=`, `mask=`, `end`.
- Keeps lease alive by sleeping half the lease, reopening the listener, and renewing.
- `timerthread` handles retransmission and state transitions.
- `stdinthread` waits for stdin EOF and sends Release before killing the process group.
- Implements option add/get helpers, packet validation, and verbose packet dump.

Important dependencies:
- Uses `dhcp.h`, Plan 9 UDP header mode, and IP formatting utilities.

Notable risks/quirks:
- Debug packet dump is unconditional in `dhcprecv` (`if(1)`).
- `stdinthread` checks `if(dhcp.client)`, but `dhcp.client` is an array and always truthy in C.
