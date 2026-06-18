# File Research: sources/os/plan9/9front/sys/src/cmd/ip/dhcpclient.c

Simple IPv4 DHCP client that broadcasts Discover, accepts Offer, sends Request, prints `ip=`, `mask=`, and `end`, then keeps the lease alive by renewing at half the lease interval.

State is held in a global locked `dhcp` struct. A timer process resends or transitions between selecting, requesting, renewing, and rebinding; a stdin watcher sends Release on shutdown.

Includes local option construction/parsing and BOOTP packet validation. Packet dump code is unconditional (`if(1)`), so received packets are always printed through `bootpdump`.
