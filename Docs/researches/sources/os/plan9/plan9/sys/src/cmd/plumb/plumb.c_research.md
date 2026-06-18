# File Research: sources/os/plan9/plan9/sys/src/cmd/plumb/plumb.c

Command-line sender for plumber messages.

Key responsibilities:
- Builds a `Plumbmsg` from command-line options and arguments or stdin.
- Sends messages to `/mnt/plumb/send` or a supplied plumb file.
- Supports attributes, source, destination, type, working directory, and stdin data.

Important behavior:
- `-i` gathers all stdin into `m.data` and defaults `action=showdata` if no action attribute exists.
- Without `-i`, each positional argument becomes one message with `ndata = -1`.
- Default source is `"plumb"` and default type is `"text"`.

Dependencies:
- Uses Plan 9 `plumbopen`, `plumbsend`, `plumbaddattr`, and `plumbunpackattr`.

Notable risks:
- Stdin collection grows with `realloc()` and has no size limit.
