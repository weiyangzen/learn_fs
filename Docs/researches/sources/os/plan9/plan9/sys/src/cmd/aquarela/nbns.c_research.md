# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/nbns.c

Implements NBNS UDP transaction transport.

Key functions:
- `udplistener` reads UDP port 137 packets, decodes NBNS messages, and routes responses to matching `NbnsTransaction` channels.
- `startlistener` lazily announces the NBNS UDP port.
- `nbnsnextid` allocates transaction ids under a lock.
- `nbnstransactionnew` serializes a request, creates a response channel, registers it, and writes the UDP packet to broadcast or unicast target.
- `nbnstransactionfree` drains pending responses, unlinks the transaction, and frees it.

Interactions:
- Used by `findname.c` and `addname.c`.
- Depends on `nbnsconv.c`, `nblistener.c`, and `nbglobals`.

Notable details:
- Only response packets are routed; request packets are currently freed.
