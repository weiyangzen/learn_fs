# File Research: sources/os/plan9/plan9/sys/src/cmd/cec/mux.c

This file multiplexes keyboard and Ethernet-console input for `cec`.

Key behavior:
- Starts one child process reading keyboard fd and another reading the network fd.
- Child processes wrap data in `Muxmsg` records tagged as keyboard, console, or fatal keyboard error.
- `mux()` creates a pipe, starts both reader processes, and returns a singleton `Mux`.
- `muxread()` reads the next multiplexed packet from the pipe.
- `muxfree()` closes fds, posts notes to both child processes, waits, and resets singleton state.

Important details:
- Only one mux can be active at a time (`smux` singleton).
- Keyboard reader reports `Ffatal` when input ends or errors.
- Console reader uses `netget()` and stops on failed pipe writes.

Filesystem relevance:
- Indirect. Coordinates fd-based console/network streams.
