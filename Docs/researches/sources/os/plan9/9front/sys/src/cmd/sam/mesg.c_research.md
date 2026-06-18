# File Research: sources/os/plan9/9front/sys/src/cmd/sam/mesg.c

`mesg.c` is the host-side sam protocol engine. It receives `Tmesg` records from `samterm`, mutates host files, and emits `Hmesg` records back to the terminal.

`rcv` incrementally parses message headers and payloads from stdin. `inmesg` dispatches terminal messages including version negotiation, command-file start, file binding/start/work selection, data requests, origin requests, typed inserts, cuts, paste/snarf, new files, writes, closes, look/search/send, double/triple-click expansion, snarf exchange, plumb, custom menu commands, ack, and exit.

The file-data protocol is lazy: terminal rasps may contain holes; `Trequest` asks the host for a range, and the host replies with `Hdata`. `Hcheck`/`Hcheck0` and `Hack` provide consistency and flow control.

`snarf` copies file ranges into a `Buffer`. `setgenstr` populates `genstr` from a range or from the snarf buffer, enforcing `TBLOCKSIZE`.

Outbound helpers (`outT0`, `outTs`, `outTslS`, etc.) serialize host messages into `outdata`; `outflush` sends buffered data and waits for `Tack` when flow-control thresholds are hit.

Plumbing support packages selected text or clicked word into a `Plumbmsg`, preserving working directory and click offset, then sends the packed message to the terminal for delivery.
