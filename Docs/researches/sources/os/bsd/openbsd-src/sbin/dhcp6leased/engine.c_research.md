# File Research: sources/os/bsd/openbsd-src/sbin/dhcp6leased/engine.c

DHCPv6 lease-state engine for `dhcp6leased`.

The engine runs as the unprivileged `_dhcp6leased` user, receives frontend/main imsgs, then tightens pledge to `stdio` after IPC setup. It maintains per-interface state machines with randomized transaction IDs, request timing, server IDs, current and candidate delegated prefixes, T1/T2/lease timers, routing domain, link state, and event timers.

It validates DHCPv6 packets from the frontend: checks header length, client ID against the daemon DUID, server ID size/duplication, IA_PD structure, IA_PREFIX lifetimes, prefix length, status codes, and required IA coverage for configured delegations. Advertise messages move `IF_INIT` to requesting; replies from requesting, renewing, rebinding, rebooting, or rapid-commit init set T1/T2/lease time and bind the lease. Renew failures with non-success IA status trigger rebinding.

State transitions implement solicit/request/renew/rebind/reboot behavior with exponential backoff, lease expiry handling, deprecation on link down, and deconfiguration on timeout or failure. On a bound lease it asks the parent to add reject routes for delegated prefixes, configure derived addresses on downstream interfaces, and write lease files. Prefix changes cause old interface configuration to be removed before new prefixes are committed.

It also formats DHCP message/option/status names, DUID hex strings, and IPv6 prefix masks. Notable limitation: config-change handling depends on `changed_ifaces()`, while the frontend implementation currently treats existing interface configs as equal.
