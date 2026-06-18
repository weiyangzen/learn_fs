# File Research: sources/os/bsd/freebsd-src/sbin/ifconfig/ifconfig.c

`ifconfig.c` is the main dispatcher for FreeBSD `ifconfig`. It owns global option parsing, address-family and command registration lists, callback deferral, interface listing, status output, address add/delete sequencing, basic interface flags/capabilities, module autoloading, jail attachment, and build-time dispatch between ioctl and netlink backends.

The command model is plugin-based: constructors in feature modules register `struct afswtch`, `struct cmd`, and options. `main()` parses global flags, handles `IFCONFIG_FORMAT`, resolves single-interface versus list mode, handles clone creation before the interface exists, detects optional address family arguments, and invokes `ifconfig_ioctl()` or `ifconfig_nl()`. In ioctl listing builds it uses `getifaddrs()`, preserves kernel order, filters by interface/group/up/down/address family, and calls per-family status hooks. In netlink builds it delegates listing to `list_interfaces_nl()`.

`ifconfig_ioctl()` interprets commands, handles clone-only command transition, treats unknown command tokens as interface/destination addresses, runs address-family post-processing, executes deferred callbacks, then performs deferred delete/add address operations. Basic commands include up/down, arp/debug/promisc/allmulti, description, alias/delete, netmask/broadcast, tunnel setup/removal, jail vnet movement, link flags, many interface capabilities, PCP, MTU, and rename.

Support helpers include group matching with shell patterns, status bit formatting, `%b`-style bit printing, VHID printing from `ifaddrs`, tunnel status fanout, metric/status printing, capability-NV packing, and module autoload guessing with explicit aliases for tun/tap/vmnet/ipsec/enc.
