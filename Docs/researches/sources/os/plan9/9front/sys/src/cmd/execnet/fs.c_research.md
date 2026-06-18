# File Research: sources/os/plan9/9front/sys/src/cmd/execnet/fs.c

This file implements the 9P filesystem served by execnet. It exposes `/exec`, `/exec/clone`, and per-client directories containing `ctl`, `data`, `local`, `remote`, and `status`.

Key responsibilities:
- Defines qid path encoding with type and client number.
- Fills directory metadata in `fillstat`.
- Generates root, exec, and connection directory entries.
- Handles reads for directories, ctl number, data stream, local pid, remote command, and status.
- Handles writes to ctl and data.
- Handles flushes by routing them to the corresponding client.
- Implements attach, walk, open, clunk handling, and request serialization.

Important implementation notes:
- Opening `clone` creates a new client and rewrites the fid to that client’s `ctl`.
- A dedicated `fsthread` serializes lib9p callbacks through channels, which simplifies shared client-state mutation and flush handling.
- `destroyfid` closes client references when opened fids are clunked.
