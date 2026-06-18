# File Research: sources/os/plan9/9front/sys/src/cmd/ip/ipconfig/dhcp.c

DHCPv4 client engine for `ipconfig`. It builds Discover/Request/Release BOOTP packets, opens UDP port 68 in header mode, tracks selecting/requesting/bound/renewing/rebinding states, retransmits with timeouts, and can spawn a watcher to renew or reacquire leases.

It validates incoming BOOTP/DHCP packets by transaction id, op, magic cookie, and option bounds. ACK processing fills local address, mask, gateway, DNS/NTP, host/domain names, lease time, server id, and Plan 9-specific vendor options for fs/auth/address/mask/gateway.

The file also defines DHCP option metadata and helpers for adding, parsing, formatting, and requesting options, including domain-name decoding through `gnames` and extra requested options stored for `/net/ndb`.
