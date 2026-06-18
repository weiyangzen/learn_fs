# File Research: sources/os/bsd/freebsd-src/sbin/route/route.c

Purpose: main implementation of the FreeBSD `route` command: add/change/delete/get/show/flush/monitor routes.

Key functions:
- `main()` parses global flags, optional jail attachment, FIB defaults, and command dispatch.
- `newroute()` parses route modifiers, destination/gateway/netmask/FIB arguments, metrics, flags, and executes per-FIB mutations.
- `rtmsg()` abstracts backend dispatch to netlink or routing socket.
- Legacy routing-socket paths include `rtmsg_rtsock()`, `flushroutes_fib_rtsock()`, and `monitor_rtsock()` when built without netlink.
- `flushroutes()` and `flushroutes_fib()` purge gateway routes by FIB and address family.
- `getaddr()`, `prefixlen()`, `inet_makemask()`, and `inet6_makenetandmask()` parse CLI address forms.
- `routename()`, `netname()`, `print_getmsg()`, `print_rtmsg()`, `pmsg_common()`, `pmsg_addrs()`, `printb()`, and `sodump()` format output and diagnostics.
- `fiboptlist_csv()` and `fiboptlist_range()` parse single, comma, range, `all`, and `default` FIB selections.

Integration: compiled with generated `keywords.h`; calls netlink functions from `route_netlink.c` unless `WITHOUT_NETLINK` is set. Uses FreeBSD routing APIs, jails, FIB sysctls, `ifaddrs`, and address-family conditionals.

Risk notes: many global parser variables are reused per invocation. FIB parsing has strict validation against `net.fibs` when available. Address parsing mutates strings temporarily for CIDR syntax. Legacy backend has explicit read timeout for `RTM_GET`.
