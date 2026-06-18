# File Research: sources/os/plan9/plan9/sys/src/9/ip/loopbackmedium.c

Implements the loopback IP medium.

Key responsibilities:
- Defines a `loopback` medium with no media header, no MAC address, and 16 KiB MTU.
- `loopbackbind` allocates per-interface state, creates a large queue, records the `Fs`, sets speed to 1000 Mbps, and starts a reader kproc.
- `loopbackbwrite` queues outgoing blocks back into the loopback queue and updates output/error counters.
- `loopbackread` drains the queue, locks the interface, and feeds packets to `ipiput4` when logical addresses exist.
- `loopbackunbind` stops the reader, waits for exit, frees queue and state.

Notable design:
- Packets loop through normal IP input processing rather than bypassing the stack.
