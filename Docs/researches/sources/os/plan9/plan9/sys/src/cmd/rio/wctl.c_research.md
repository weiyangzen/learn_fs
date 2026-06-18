# File Research: sources/os/plan9/plan9/sys/src/cmd/rio/wctl.c

Read status: complete, 515 lines.

`wctl.c` parses and applies `rio` window control commands. It supports commands such as `new`, `resize`, `move`, `scroll`, `noscroll`, `set`, `top`, `bottom`, `current`, `hide`, `unhide`, and `delete`, with parameters for rectangle, pid, id, hidden state, scrolling state, and working directory.

`parsewctl` tokenizes command strings and computes the target rectangle. `goodrect` enforces minimum, canonical, and manageable window geometry. `writewctl` applies commands written to a window’s `wctl` file. `wctlproc` reads commands from the global wctl pipe and `wctlthread` applies global `new` requests.

Filesystem relevance: this is the command parser behind `/dev/wctl` and the global `/srv/riowctl.*` interface.
