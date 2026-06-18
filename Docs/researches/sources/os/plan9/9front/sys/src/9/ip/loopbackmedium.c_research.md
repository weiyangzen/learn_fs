# File Research: sources/os/plan9/9front/sys/src/9/ip/loopbackmedium.c

Implements the loopback IP medium.

Key elements:
- Creates a large message queue for loopback packets.
- Starts a `loopbackread` kernel process to feed queued packets into `ipiput4`.
- Writes enqueue packets directly onto the loopback queue.
- Registers a `Medium` named `loopback`.

Dependencies:
- Used by `ipifc.c` for local delivery and as auxiliary loopback support for other media.

Research notes:
- The read path processes through the IPv4 input function, which also handles version dispatch in this stack.
