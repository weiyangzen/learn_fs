# File Research: sources/os/plan9/9front/sys/src/9/ip/chandial.c

Provides a kernel helper for dialing Plan 9 network device conversations from a dial string. It parses strings of the form `[/net/]proto!dest`, opens the protocol clone file, writes a `connect` control message, and returns the data channel.

Key responsibilities:
- Parses dial strings in `_dial_string_parse()`.
- Defaults the network directory to `/net` if absent.
- Opens `<netdir>/<proto>/clone`, reads the allocated conversation number, and constructs the conversation path.
- Writes `connect <dest>` or `connect <dest> <local>` to the control channel.
- Opens and returns the conversation `data` channel.

Important implementation details:
- `DS` stores parsed dial-string components and output pointers for the control channel and directory path.
- If `ctlp` is supplied, ownership of the open control channel is returned to the caller; otherwise it is closed.
- `dir`, if supplied, receives the concrete conversation directory path.
- Uses direct `devtab[type]->read/write` on the clone/control channel.

Dependencies and integration:
- Used by media code such as `ethermedium.c` to bind Ethernet ethertype conversations.
- Depends on Plan 9 namespace/device APIs: `namec`, `cclose`, `devtab`.

Research notes:
- This is a small compatibility/convenience layer, not a protocol implementation.
- There is no connection server translation here; it directly targets the Plan 9 network device namespace.
