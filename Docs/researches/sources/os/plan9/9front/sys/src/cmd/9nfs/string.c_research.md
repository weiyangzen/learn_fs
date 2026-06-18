# File Research: sources/os/plan9/9front/sys/src/cmd/9nfs/string.c

Permanent string interning table for 9nfs.

Key responsibilities:
- `strfind()` looks up an already-interned string.
- `strstore()` interns strings and returns stable storage.
- `strprint()` dumps hash buckets for diagnostics.
- Allocates `Strnode` objects from permanent chunk storage.

Important behavior:
- Hash buckets are move-to-front on lookup/store hits.
- Storage is never individually freed; chunks grow from `STRSIZE` upward to fit large strings.
- String payloads are 4-byte aligned inside `Strnode` allocations.

Dependencies:
- Uses `Strnode` from shared headers and Plan 9 allocation/logging helpers.

Notable risks:
- Unbounded lifetime is intentional for daemon caches, but dynamic or hostile names can grow memory permanently.
