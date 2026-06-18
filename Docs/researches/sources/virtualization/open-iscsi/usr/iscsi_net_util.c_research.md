# File Research: sources/virtualization/open-iscsi/usr/iscsi_net_util.c

This file provides network utility functions used by iSCSI iface and boot/offload setup. It maps NIC drivers to iSCSI transports, resolves MAC-to-netdev binding, identifies VLAN devices, validates IP versions, brings interfaces up, assigns firmware boot addresses, and installs host routes to target portals.

Major responsibilities:
- Maintains a driver-to-iSCSI-transport table:
  - `cxgb3` to `cxgb3i`
  - `cxgb4` to `cxgb4i`
  - `bnx2`/`bnx2x` to `bnx2i`
- `net_get_transport_name_from_netdev()` uses `ETHTOOL_GDRVINFO` to find the NIC driver and maps it to an iSCSI offload transport. For bnx2/bnx2x, it requires the `iscsiuio` executable to exist.
- `net_get_netdev_from_hwaddress()` iterates interfaces, reads Ethernet hardware addresses with `SIOCGIFHWADDR`, and returns the first matching netdev.
- `find_vlan_dev()` scans interfaces and returns a VLAN device name matching a requested VLAN ID.
- `net_get_ip_version()` uses numeric `getaddrinfo()` to classify an IP string as IPv4 or IPv6.
- `net_setup_netdev_ipv4()` brings up physical/VLAN interfaces, sets IPv4 address and netmask when needed, and adds a host route to the target, using a gateway when target and local address are on different subnets.
- `net_setup_netdev_ipv6()` brings up physical/VLAN interfaces, sets IPv6 address/prefix when needed, and adds a host route through the gateway.
- `net_ifup_netdev()` brings an existing netdev up if not already up.

Important dependencies:
- Uses ioctl APIs: `SIOCETHTOOL`, `SIOCGIFHWADDR`, `SIOCGIFVLAN`, `SIOCSIFFLAGS`, `SIOCSIFADDR`, `SIOCSIFNETMASK`, and `SIOCADDRT`.
- Uses Linux networking headers for VLAN, Ethernet, IPv6 route, and socket ioctls.
- Uses `ethtool-copy.h`, `iscsi_net_util.h`, `sysdeps.h`, and logging helpers.

Filesystem/storage relevance:
- This is support code for firmware boot and offload iSCSI paths, ensuring the correct NIC/VLAN/address/route exists before login to remote storage.

Notable constraints and risks:
- VLAN handling only finds an existing VLAN device; it does not create one.
- MAC-to-netdev matching does not support bonds/aliases with duplicate hardware addresses.
- `find_vlan_dev()` appears to issue an initial `SIOCGIFHWADDR` without first assigning an interface name to `if_hwaddr`, so that path deserves careful verification.
- IPv6 setup requires a gateway string and always builds a gateway route.
