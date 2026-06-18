# File Research: sources/os/plan9/plan9/sys/src/cmd/fossil/fossil.c

Main fossil server entry point.

It isolates the process environment with `rfork`, redirects stdio to `/dev/null`, attaches Venti support, parses console commands from `-c` and from a fossil config partition via `-f`, initializes console, CLI, 9P message handling, fsys, exclusives, fids, srv/listener/user subsystems, then executes startup commands. With `-t`, it attaches an interactive raw console.

`readCmdPart` reads configuration commands from a fixed offset before the fossil header and expands a standalone `*` argument to the current partition path.
