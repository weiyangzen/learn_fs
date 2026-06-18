# File Research: sources/os/bsd/freebsd-src/sbin/ifconfig/ifvxlan.c

`ifvxlan.c` implements VXLAN configuration. It registers clone-time and runtime VXLAN identity/address/port/learning commands, flush commands, VXLAN hardware capability toggles, status reporting, and a `vxlan` clone callback.

The file uses static `struct ifvxlanparam params` for clone-time accumulation. `vxlan_exists()` probes driver config with `VXLAN_CMD_GET_CONFIG`; setters update `params` before creation or send an immediate `SIOCSDRVSPEC` driver command after creation.

`vxlan_status()` fetches `struct ifvxlancfg`, suppresses output when VNI is unset, formats local and remote/group addresses with numeric host/service output, detects multicast group addresses, and in verbose mode prints learning, port range, TTL, and forwarding-table counters/limits.

Setters validate VNI, local/remote/group addresses, local and remote UDP ports, source port range, forwarding-table timeout and max address count, multicast device, TTL, and learning state. Address parsing uses `getaddrinfo()` and rejects multicast local/remote addresses while requiring multicast for `vxlangroup`.

`vxlan_check_params()` prevents mixed IPv4/IPv6 local/remote clone parameters and duplicate IPv4+IPv6 local or remote specifications. `vxlan_create()` validates and passes accumulated params to `ifcreate_ioctl()`.

Notable edge behavior: numeric parsing uses `strtoul()` with `ERANGE` checks. Port validation rejects values `>= UINT16_MAX`, so `65535` is not accepted as a port. TTL allows values through 256, matching the local implementation’s accepted range.
