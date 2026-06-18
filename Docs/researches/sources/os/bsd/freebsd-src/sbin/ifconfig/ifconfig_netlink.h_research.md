# File Research: sources/os/bsd/freebsd-src/sbin/ifconfig/ifconfig_netlink.h

`ifconfig_netlink.h` is a small conditional include wrapper for netlink support. When `WITHOUT_NETLINK` is not defined, it includes the core FreeBSD netlink headers, route netlink headers, simple-netlink helper API, route compatibility helpers, and route parsers.

Modules include this header to share netlink parser/writer types while keeping non-netlink builds free of those dependencies.
