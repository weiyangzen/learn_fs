# File Research: sources/os/bsd/openbsd-src/sbin/route/route.c

This file is the main implementation of OpenBSD `route`. It parses commands, builds routing socket messages, mutates routes and source-address settings, flushes routing tables, submits resolver proposals, monitors routing events, and prints verbose routing-message diagnostics.

Key APIs:
- `main()`: parses global flags, opens `AF_ROUTE`, applies route table/message filters, pledges, and dispatches `show`, `flush`, `sourceaddr`, `get`, `add`, `change`, `delete`, `monitor`, and `nameserver`.
- `flushroutes()`: dumps routes via sysctl and deletes matching non-interface routes by family, interface, and priority.
- `newroute()`: parses route command modifiers, destination/gateway/netmask/prefix/label/MPLS/metrics/BFD/priority options, then calls `rtmsg()`.
- `setsource()` and `pushsrc()`: set preferred source address globally or from an interface address.
- `nameserver()`: sends `RTM_PROPOSAL` DNS server proposals for an interface.
- `rtmsg()`: constructs `struct rt_msghdr` plus ordered sockaddr payloads and writes it to the route socket.
- `getaddr()`, `prefixlen()`, `getmplslabel()`, `getlabel()`, `sockaddr()`: parse user address inputs into `union sockunion` globals.
- `print_rtmsg()`, `print_getmsg()`, `pmsg_addrs()`, `bprintf()`: verbose route-message decoders.
- BFD helpers under `#ifdef BFD`: state, diagnostic, uptime, and sockaddr-BFD printing.

Behavior and integration:
- Shares display helpers and `union sockunion` with `show.c` through `show.h`.
- Uses route socket messages, `sysctl NET_RT_DUMP`, `ROUTE_TABLEFILTER`, `ROUTE_MSGFILTER`, routing domains, OpenBSD route priorities, MPLS labels, route labels, and proposal sockaddrs.
- Supports `pledge()` transitions from route privileges to narrower stdio/dns modes after socket setup.
- `-t` sends route messages to `/dev/null` for test/debug output.
- `RTM_GET` waits for a matching version/sequence/pid reply and prints a route report.

Risk notes:
- Many parser decisions mutate global state (`rtm_addrs`, `so_*`, `aflen`, `forcehost`, `forcenet`, `mpls_flags`), so command parsing is order-sensitive.
- `rtmsg()` uses a fixed 512-byte sockaddr payload area; unusual combinations depend on kernel sockaddr sizes fitting.
- Proposal printing validates embedded lengths for DNS/static/search payloads, but regular route-message sockaddr traversal trusts kernel-provided lengths.
- Compatibility code retains unused metrics and older syntax, increasing parser surface.
