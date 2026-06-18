# File Research: sources/os/plan9/9front/sys/src/cmd/9nfs/nametest.c

This utility tests Unix ID-map parsing and name/id lookup behavior.

Key behavior:
- With no arguments, reads Unix IDs from stdin using selected style (`-9` or `-u`) and prints them.
- With a config file, loads maps, selects a default or requested client, and accepts interactive commands from stdin.
- Commands switch user/group maps, reload maps, lookup id-to-name and name-to-id, print current server/client, and dump IDs.

Key routines:
- `main` parses options and command loop.
- `mapinit` reads mapping files and selects a `Unixidmap` using `pair2idmap`.

Important interactions:
- Uses mapping functions declared in `fns.h`.
- Uses `chatty` and `rpcdebug` globals for debugging compatibility.

Research notes:
- Default test client is hard-coded as `nslocum.research.bell-labs.com`; default server in lookup is `bootes`.
