# File Research: sources/os/plan9/9front/sys/src/cmd/aux/flashfs/dreq.c

Role: Simplified/debug 9P request server for flashfs entries.

Behavior:
- Provides attach, walk, open, create, read, write, remove, stat, and wstat over the in-memory `Entry` tree.
- Enforces mode bits and readonly checks, but write handling only validates size and acknowledges count; it does not journal file data like `request.c`.
- Directory reads use `edirread`; file reads return count zero in this variant.
- `serve` initializes the entry tree with `einit()` and mounts service `brzr` at the requested mount point.

Differences from `request.c`:
- No `need`, `put`, or `putw` journal emission for create/write/remove/chmod/truncate.
- `walk` incorrectly rejects all walking when readonly is set, unlike the active server.
- Useful as a debug or early skeleton, not the complete persistent filesystem path.
