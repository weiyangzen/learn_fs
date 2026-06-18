# File Research: sources/os/plan9/plan9/sys/src/9/ip/netdevmedium.c

Implements a generic network-device IP medium over an already-openable Plan 9 channel path.

Key responsibilities:
- Defines `netdev` medium with no media header, 64 KiB MTU, and persistent binding.
- `netdevbind` opens the supplied path `ORDWR`, stores the channel and `Fs`, and starts a reader process.
- `netdevbwrite` concatenates/pads outgoing blocks and writes them directly to the device channel.
- `netdevread` reads packets from the channel and passes them to `ipiput4`; if read returns nil, it attempts to unbind the interface and exits.
- `netdevunbind` posts a note to the reader, waits for exit, closes the channel, and frees state.

Notable use:
- Provides a generic packet-device bridge without Ethernet/ARP framing behavior.
