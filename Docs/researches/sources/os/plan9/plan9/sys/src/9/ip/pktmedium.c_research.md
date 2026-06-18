# File Research: sources/os/plan9/plan9/sys/src/9/ip/pktmedium.c

Implements a synthetic packet medium for user-visible packet injection and capture.

Key responsibilities:
- Defines `pkt` medium with Ethernet-like header sizing, 4 KiB MTU, MAC length 6, write hook, and `pktin` hook.
- Bind/unbind are no-ops.
- `pktbwrite` concatenates outbound packets, optionally copies them to the conversation snoop queue, then queues them to the conversation read queue.
- `pktin` handles packets written to interface `data`: drops if no logical interface exists, optionally snoops, and injects into normal IPv4 input via `ipiput4`.
- `pktmediumlink` registers the medium.

Notable use:
- Useful for packet-level testing or user-space packet handling through `ipifc` conversations and `snoop`.
