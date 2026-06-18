# File Research: sources/os/plan9/9front/sys/src/cmd/aux/flashfs/request.c

Role: Main lib9p request implementation for persistent flashfs.

State:
- Each fid gets a `State` containing current `Entry` and optional directory reader.
- `destroy` drops entry refs and closes directory readers; auth fids with nil state are tolerated.

Operations:
- `flattach` attaches to root.
- `flopen` enforces permissions, rejects write opens on directories, opens directory readers, and journals truncation when `OTRUNC` is used.
- `flcreate` validates directory/write permission/name length, reserves journal space, creates the entry, and emits `FT_create`.
- `flread` reads directories through `edirread` and files through `eread`.
- `flwrite` chunks writes by `maxwrite`, reserves journal room, creates extents, updates entry state, and emits `FT_WRITE` with data through `putw`.
- `flremove` journals `FT_REMOVE` after successful entry removal.
- `flwstat` supports mode changes through `FT_chmod`.
- `flwalk` walks namespace and handles partial walk errors in Plan 9 style.

Serving:
- `serve` fills a static `Srv`, installs request handlers, and mounts service `brzr` with `MREPL|MCREATE`.

Important constraints:
- Rejects writes at or beyond `MAXFSIZE`.
- Rejects writes when `used + count > limit`.
- Readonly blocks mutating operations but not walks.
