# File Research: sources/os/plan9/plan9/sys/src/9/ip/chandial.c

Kernel channel-based dial helper for Plan 9 network clone/data interfaces.

Key behavior:
- Parses dial strings of form `[/net/]proto!dest`.
- Defaults net directory to `/net` and proto to `net` when no `!` exists.
- Opens `<netdir>/<proto>/clone`, reads clone instance number, optionally returns control directory and control channel.
- Writes `connect <dest> [local]` to the control channel.
- Opens and returns the associated `data` channel with `ORDWR`.
- If caller does not request the control channel, it closes it.

This is an in-kernel analogue of userland dial behavior using `Chan` and `devtab` operations.
