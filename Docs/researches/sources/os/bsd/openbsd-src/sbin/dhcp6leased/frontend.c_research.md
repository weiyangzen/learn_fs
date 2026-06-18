# File Research: sources/os/bsd/openbsd-src/sbin/dhcp6leased/frontend.c

Unprivileged network frontend for `dhcp6leased`.

The frontend drops to `_dhcp6leased`, pledges `stdio unix recvfd route`, receives sockets and configuration from the parent, monitors interface route messages, owns per-interface UDP receive events, and sends/receives DHCPv6 packets. It builds vendor-class data from `uname()`, sets the multicast destination to `ff02::1:2` on server port 547, and requests bound UDP sockets from the parent for configured, running interfaces.

Configuration is reconstructed from imsg streams into local SIMPLEQ structures. On reconfiguration it computes changed interfaces, updates them, and asks the engine to reboot DHCP processing. Interface route messages trigger updates or removal; UDP packets are wrapped in `IMSG_DHCP` and forwarded to the engine.

Outbound packets are built for solicit, request, renew, and rebind. The packet builder writes client ID, optional server ID, IA_PD/IA_PREFIX options for each configured IA, option request options, elapsed time, optional rapid commit, and vendor class. If the engine asks to send before the UDP socket arrives, the interface records a pending solicit and sends once `set_udpsock()` installs the event.

Notable limitation: `iface_conf_cmp()` currently always returns `0`, so changed existing interface details are not detected by that comparison path.
