# File Research: sources/os/plan9/9front/sys/src/cmd/samterm/mesg.c

`mesg.c` is samterm's terminal-side protocol implementation. It parses `Hmesg` packets from the host, updates menu/text/rasp/layer state, and serializes `Tmesg` packets back to the host.

`rcv` incrementally parses host packets and calls `inmesg`. `inmesg` handles version, bind/current/move/new names, grow/cut/data/origin/check/unlock/setdot/moveto/clean/dirty/delete/close/pattern/snarf/ack/exit/plumb/menu-command messages.

Text synchronization is lazy and lock-aware. `hgrow`, `hdata`, `hdatarune`, and `hcut` update the terminal `Rasp` plus all open layers for a text. `hcheck` finds visible holes or missing end-of-frame text and sends `Trequest`/`Tcheck` while incrementing text locks.

`horigin`, `hmoveto`, and `hsetdot` update frame origins and selections. `flnewlyvisible` triggers `hcheck` when a previously hidden layer becomes visible.

`setlock`/`clrlock` manage host lock state and cursor changes. `startfile` and `startnewfile` initiate host binding for existing or new windows.

Outbound helpers serialize terminal messages with short, long, vlong, strings, and raw payloads. `hsetsnarf` swaps sam's snarf buffer with `/dev/snarf`; `hplumb` unpacks host-provided plumb data and sends it to the plumb port.
