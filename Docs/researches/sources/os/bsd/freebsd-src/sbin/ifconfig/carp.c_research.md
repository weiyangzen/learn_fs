# File Research: sources/os/bsd/freebsd-src/sbin/ifconfig/carp.c

`carp.c` implements CARP and VRRP configuration/status integration for `ifconfig` using `libifconfig`. It registers CARP/VRRP commands and an `AF_UNSPEC` status hook.

Status reads up to `CARP_MAXVHID` entries and prints CARP state, VHID, advbase, advskew, optional key, IPv4/IPv6 peers, or VRRP state, VRID, priority, and interval. Setters collect command-line values in file-scope state and defer application via `setcarp_callback()` registered when `vhid` is set.

Commands cover `vhid`, password, advskew/base, state, peer/mcast IPv4, peer6/mcast6 IPv6, CARP/VRRP version, VRRP priority, and VRRP advertisement interval. The callback fetches an existing VHID entry if present, overlays requested fields, and writes it with `ifconfig_carp_set_info()`.
