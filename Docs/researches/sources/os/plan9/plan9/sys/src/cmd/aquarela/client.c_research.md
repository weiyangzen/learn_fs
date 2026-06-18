# File Research: sources/os/plan9/plan9/sys/src/cmd/aquarela/client.c

Standalone NetBIOS name registration client.

Key functions:
- `warning` logs to syslog and optionally stdout.
- `udpannounce` announces the `netbios-ns` UDP service and enables Plan 9 UDP header mode.
- `listen137` reads UDP NBNS packets, decodes them, dumps them, and routes responses to matching transactions.
- `threadmain` parses optional unicast server IP, builds a NetBIOS name, initializes network/broadcast state, starts listener, and calls `nbnsaddname`.

Interactions:
- Uses NBNS transaction globals and message conversion/dump routines.
- Overlaps with the reusable `nbns.c` logic but contains its own listener-oriented test harness.

Notable details:
- The `udpannounce` write check uses `if(write(...) , 0)`, which always evaluates false; this looks like an old bug or disabled assertion.
