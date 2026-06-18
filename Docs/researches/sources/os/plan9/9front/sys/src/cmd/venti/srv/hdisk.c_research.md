# File Research: sources/os/plan9/9front/sys/src/cmd/venti/srv/hdisk.c

HTTP disk inspection and score-debug support for the Venti admin server.

Key behavior:
- `/disk` without args lists arena partitions, index sections, and Bloom partition from `mainindex`.
- `/disk?disk=...&type=a` opens an arena partition read-only, decodes the arena-part header/table, lists arenas, or inspects a selected arena.
- Arena inspection decodes header/tail, prints stats, and either lists clump-info TOC, finds a score in the TOC, or decodes a clump by offset.
- `diskarenaclump` reads a clump, tries alternate magic if magic mismatch, decompresses when needed, and recomputes score.
- `hdebug` supports `op=amap`, `op=mem`, and `op=read`.
- `debugread` compares icache, on-disk index, lookupscore, arena mapping, and clump load results for a score; optional brute-force arena search.

Interactions:
- Registered by `httpd.c` at `/disk` and `/debug`.
- Uses `initpart`, unpackers, `icachelookup`, `loadientry`, `lookupscore`, `amapitoa`, `loadclump`, and `findintoc`.

Notable details:
- `diskbloom` and `diskisect` are stubs.
- The `disk` query parameter is opened as a path with no visible authorization in this file; trust depends on how the admin HTTP service is exposed.
