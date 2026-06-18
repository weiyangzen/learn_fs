# File Research: sources/os/plan9/9front/sys/src/cmd/ip/rip.c

This is a RIP v1 routing daemon for IPv4. It receives RIP responses, maintains an in-memory route table, installs/removes routes through `/net/iproute`, and optionally broadcasts route updates.

The code defines RIP wire structs, route table storage, interface metadata, and broadcast-network selection. `main` parses broadcast/debug/read-only/net options plus optional specific broadcast networks, backgrounds unless debugging, reads interfaces and existing routes, opens UDP port `rip` in header mode, then loops receiving RIP messages.

`readifcs` uses `readipifc` to discover IPv4 interfaces, masks, direct networks, and broadcast eligibility. `readroutes` seeds internal state from `/net/iproute`, preserving an immutable default route.

`considerroute` hashes routes by class network, rejects attempts to hijack the default route, replaces stale or worse existing routes, and installs better routes. `installroute` and `removeroute` write textual commands to `/net/iproute` unless read-only mode is active.

`broadcast` refreshes interfaces and calls `sendto` for each broadcast network. `sendto` applies split-horizon-like filtering, avoids advertising a network to itself, avoids leaking subnet routes across classful boundaries, and emits RIP response packets. `timeoutroutes` expires non-infinite routes after ten minutes without refresh.

The implementation is classful and IPv4-only, matching RIP v1 expectations.
