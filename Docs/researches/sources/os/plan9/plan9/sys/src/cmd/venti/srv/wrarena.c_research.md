# File Research: sources/os/plan9/plan9/sys/src/cmd/venti/srv/wrarena.c

Purpose: Replays/copies clumps from an arena file into a Venti server.

Key behavior:
- Opens an arena file, initializes the arena, optionally connects to a Venti server, and starts multiple sender threads.
- `rdarena` walks clump directory entries, skips corrupt clumps and optional initial offsets, loads clumps, validates score/type unless `-f`, and sends valid clumps to sender threads.
- Sender threads call `vtwrite` and free zblocks.
- Supports host override, fast mode, max writes, verbose scores, and offset reporting.

Dependencies:
- Uses arena loading, clump info reads, `vtwrite`, `vtsync`, Venti connection APIs, channels, and stats/dcache initialization.

Notable details:
- Host `/dev/null` suppresses server connection and just reads/validates.
- Sender threads intentionally block at exit as a workaround for historical libthread/NPTL shutdown trouble.
