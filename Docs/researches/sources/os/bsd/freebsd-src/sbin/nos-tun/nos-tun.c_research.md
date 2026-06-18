# File Research: sources/os/bsd/freebsd-src/sbin/nos-tun/nos-tun.c

Legacy IP-over-IP tunnel helper for configuring a `tun` interface and forwarding packets through a raw socket using NOS/Cisco-style encapsulation.

Key behaviors:
- Resolves source/destination/target addresses with `inet_addr()` or `gethostbyname()`.
- Opens a tun device, clears prior interface address, assigns point-to-point source/destination addresses, and marks interface up.
- Opens a raw IPv4 socket with protocol 94 by default or user-provided `-p`.
- Optionally binds a raw socket source address.
- Daemonizes, installs signal handlers, and loops with `select()` over tun and raw socket descriptors.
- Packets from raw socket are accepted only from the configured target, decapsulated by skipping the outer IP header, and written to tun.
- Packets from tun are sent to the connected raw socket target.
- Signal cleanup brings the interface down and removes addresses.

Research notes:
- Uses old IPv4-only APIs (`gethostbyname`, `inet_addr`) and global interface request state.
- Does not robustly validate packet lengths before subtracting IP header length.
