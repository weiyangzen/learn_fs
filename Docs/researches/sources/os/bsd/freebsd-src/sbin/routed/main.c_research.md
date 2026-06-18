# File Research: sources/os/bsd/freebsd-src/sbin/routed/main.c

Main daemon entry point, option parsing, socket setup, signal handling, timer scheduling, and event loop.

Key responsibilities:
- Parses daemon flags for supplier/quiet mode, default-route advertisement, multihomed host routes, tracing, auth behavior, fake routes, and parameter overrides.
- Checks root privileges and kernel IP forwarding state, disabling supplier behavior when forwarding is off.
- Daemonizes unless debugging, opens syslog, routing socket, RIP sockets, trace output, buffers, and radix table state.
- Initializes timing epoch and randomizes broadcast/router-discovery intervals.
- Reads `/etc/gateways`, discovers interfaces, sends initial RIP queries, and sends router-discovery solicitations.
- Runs a single-threaded `select()` loop over routing, RIP, per-interface RIP, and router-discovery sockets.
- Drives interface rescans, kernel route flush checks, periodic RIP broadcasts, flash updates, route aging, kernel sync, and router discovery.
- Provides helpers for select fd rebuilding, socket option setup, RIP socket on/off behavior, allocation, random intervals, timeval math, and logging.

Dependencies:
- Coordinates nearly every routed subsystem: interface manager, route table, RIP input/output, router discovery, trace, parameters, and kernel routing socket.

Notable risks:
- Time monotonicity is simulated with a microsecond fudge; timer ordering depends on this invariant.
- Signal handlers only set simple state, but shutdown triggers final RIP/router-discovery advertisements.
- Main loop behavior changes substantially depending on `supplier`, router discovery, forwarding, and interface counts.
