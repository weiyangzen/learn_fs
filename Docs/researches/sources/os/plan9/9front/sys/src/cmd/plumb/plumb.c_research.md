# File Research: sources/os/plan9/9front/sys/src/cmd/plumb/plumb.c

`plumb.c` is the command-line message sender. It builds a `Plumbmsg` from options for attributes, source, destination, type, working directory, and either argv data items or stdin data with `-i`.

By default it opens the `send` port with `plumbopen()`, or a specified plumb file with `-p`, and sends each message via `plumbsend()`. For stdin messages it defaults the `action=showdata` attribute when no action is present.
