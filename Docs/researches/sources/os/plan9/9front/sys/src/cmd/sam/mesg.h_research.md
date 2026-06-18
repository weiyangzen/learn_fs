# File Research: sources/os/plan9/9front/sys/src/cmd/sam/mesg.h

`mesg.h` defines the sam host-terminal wire protocol. `VERSION` is 4, reflecting plumbing, larger snarf buffers, triple click, and `M` menu-command support.

It defines message size constants: `TBLOCKSIZE` for largest text piece sent to the terminal, `DATASIZE` for encoded packet capacity, and `SNARFSIZE` for exchanged snarf text.

`Tmesg` enumerates terminal-to-host messages for versioning, file/window start, check/request/origin, typing/cut/paste/snarf/write/close/look/search/send, click expansion, snarf exchange, acks, exit, plumbing, and custom menu commands.

`Hmesg` enumerates host-to-terminal messages for versioning, menu/file binding/current/name movement, rasp grow/cut/data/check/origin, unlocks, dot/moveto, clean/dirty state, close, snarf, ack, exit, plumb, and custom menu updates.

The trailing comment records a protocol model for the grow/data/check/request interaction and notes a Spin proof for lack of non-progress cycles.
