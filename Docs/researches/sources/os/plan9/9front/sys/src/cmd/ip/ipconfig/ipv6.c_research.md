# File Research: sources/os/plan9/9front/sys/src/cmd/ip/ipconfig/ipv6.c

IPv6 configuration support for `ipconfig`. It initializes RA defaults, parses static prefix and RA parameters, derives link-local addresses from Ethernet addresses, adds IPv6 addresses with duplicate-neighbor detection, and configures kernel RA parameters.

Host-side RA handling listens for router advertisements, processes link-layer address, MTU, prefix, RDNSS/DNSSL, and Plan 9 fs/auth options, manages learned route/prefix lifetimes, updates `/net/ndb`, refreshes cs/dns, and invokes DHCPv6 when the managed flag is set.

Router-side support sends router advertisements, responds to router solicitations, includes current global prefixes and ndb-derived DNS/fs/auth/domain options, sends final zero-lifetime RAs when disabled, and coordinates send/receive RA daemons.
