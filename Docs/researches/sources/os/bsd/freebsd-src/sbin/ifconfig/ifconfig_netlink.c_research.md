# File Research: sources/os/bsd/freebsd-src/sbin/ifconfig/ifconfig_netlink.c

`ifconfig_netlink.c` provides the netlink backend for `ifconfig`. It opens a `NETLINK_ROUTE` socket, attempts to load the `netlink` kernel module if needed, wraps single-interface configuration through `ifconfig_nl()`, and implements netlink-based interface listing/status.

The listing path builds an ifindex-indexed `ifmap` from `RTM_GETLINK`, resolves names with a targeted `RTM_GETLINK`, dumps addresses with `RTM_GETADDR`, attaches parsed addresses to interfaces, sorts interfaces in kernel-provided order, sorts addresses by family and original order, applies interface/name/group/up/down/address-family filters, and then prints either names or full status.

Status output prints flags, metric, MTU, description, capabilities, tunnel status, link-level address, address-family statuses, other status hooks, driver name, interface status text, and optional SFP data. Link and address parsing relies on `netlink_snl_route` parser structures shared with address-family modules.
