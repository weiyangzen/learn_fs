# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/nbdgram.c

Implements NetBIOS datagram service listener registration, packet dispatch, and send support.

Key functions:
- `udplistener` reads UDP datagrams, decodes `NbDgram`, filters unsupported fragments, validates destination names, and dispatches to registered listeners.
- `startlistener` lazily announces UDP port 138.
- `nbdgramlisten` registers a destination-name listener and records local names.
- `nbdgramsendto` encodes and writes a datagram to a target IP/port.
- `nbdgramsend` resolves or broadcasts destination names and fills source/destination datagram fields.

Interactions:
- Used by SMB browser/mailslot announcements.
- Depends on `nbdgramconv.c`, `nblistener.c`, `nbname.c`, and `nbresolve.c`.

Notable details:
- Fragmented datagrams (`More` flag or nonzero offset) are ignored.
- Listener callback return values control one-shot removal or continued listening.
