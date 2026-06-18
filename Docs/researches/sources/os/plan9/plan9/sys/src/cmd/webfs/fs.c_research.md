# File Research: sources/os/plan9/plan9/sys/src/cmd/webfs/fs.c

This file implements the `webfs` 9P filesystem surface, conventionally mounted at `/mnt/web`.

Filesystem layout:
- Root files: `ctl`, `clone`, `cookies`.
- Per-client directories named by client number.
- Per-client files: `ctl`, `body`, `body.<ext>`, `contenttype`, `postbody`, `parsed/`.
- `parsed/` exposes URL fields: `url`, `scheme`, `schemedata`, `user`, `passwd`, `host`, `port`, `path`, `query`, `fragment`, `ftptype`.

Qid model:
- Low 8 bits are type; upper bits encode client number.
- `PATH(type, n)`, `TYPE(path)`, and `NUM(path)` pack/unpack.

Directory/stat:
- `fillstat` names files and synthesizes `body.<ext>`.
- `rootgen`, `clientgen`, and `parsedgen` generate directory listings.

Read/write/open:
- `fsread` handles directory reads, global/client ctl reads, cookie reads, content type/post body reads, body reads via per-client worker, and parsed URL field reads.
- `fswrite` handles cookie writes, ctl command parsing/dispatch, and `postbody` writes with a 128 MB offset sanity cap.
- `fsopen` enforces mode bits, initializes cookie editing, increments client refs, opens body through the client worker, and implements `clone` by creating a new client and redirecting the fid to its ctl file.
- `fswalk1` implements manual walking through root/client/parsed directories and dynamic `body.<ext>` names.

Concurrency:
- `fsthread` serializes most 9P operations through channels, coordinates clunks, starts plumbing, and forwards body I/O to per-client workers.
- `fsflush` routes body open/read flushes to the client worker and interrupts its I/O proc.
- `fssend` serializes lib9p callbacks by sending requests to `fsthread` and waiting on `creqwait`.

Shutdown:
- `takedown` closes cookies and exits all threads.

Notable behavior:
- The implementation avoids direct handling of spurious flushes by making lib9p callbacks synchronous through `fssend`.
- Body reads/open are guarded by `c->iobusy` to prevent overlapping I/O per client.
