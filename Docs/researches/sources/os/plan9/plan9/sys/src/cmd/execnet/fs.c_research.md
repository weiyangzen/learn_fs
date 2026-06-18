# File Research: sources/os/plan9/plan9/sys/src/cmd/execnet/fs.c

9P filesystem implementation for `execnet`.

Key behavior:
- Exposes `/exec`, `/exec/clone`, and per-client directories containing `ctl`, `data`, `local`, `remote`, and `status`.
- Encodes qid paths with object type and client number.
- Implements stat generation, directory generators, reads, writes, flushes, attach, walk, open, and fid destruction.
- Opening `clone` allocates a new client and retargets the fid to that client’s `ctl`.
- `data` reads/writes delegate to `client.c`; metadata files expose pid, command, and status.
- Serializes lib9p callbacks through `fsthread` channels to simplify flush/clunk coordination.

Filesystem relevance:
- Defines the synthetic file tree and 9P behavior for executing commands through a network-like interface.
