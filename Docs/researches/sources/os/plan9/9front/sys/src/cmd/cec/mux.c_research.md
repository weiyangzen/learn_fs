# File Research: sources/os/plan9/9front/sys/src/cmd/cec/mux.c

Two-source multiplexer for keyboard and CEC network input.

Key behavior:
- Defines `Muxmsg` with a source type and embedded `Pkt`.
- `muxcec` reads packets from `netget` and forwards them to a pipe tagged as `Fcec`.
- `muxkbd` reads keyboard bytes, packs them into `Pkt.data`, and forwards them tagged as `Fkbd`; sends `Ffatal` on EOF.
- `muxproc` forks worker processes for each input source.
- `mux` initializes a singleton mux with one keyboard worker and one CEC worker.
- `muxread` reads tagged events and copies packet data out.
- `muxfree` closes pipes, posts notes to workers, waits, and resets singleton state.

Dependencies:
- Includes `cec.h` and Plan 9 process/pipe APIs.

Research notes:
- The singleton `smux` means only one mux instance can be active.
