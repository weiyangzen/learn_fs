# File Research: sources/os/plan9/9front/sys/src/cmd/gefs/fs.c

Main gefs 9P server, mutation pipeline, snapshot sync, permission logic, and background admin tasks.

Key responsibilities:
- Implements 9P attach, auth, walk, open, create, read, write, stat, wstat, remove, clunk, flush, and version handling.
- Maintains mounts, fids, directory-entry cache, per-connection fid tables, auth fids, and synthetic dump-root behavior.
- Routes requests through separate reader, mutator, admin/sweeper, sync, and periodic-task queues.
- Performs COW B-tree updates for file writes, directory changes, metadata changes, truncation, and removal.
- Coordinates snapshot updates, ordered sync passes, arena header/superblock writes, deadlist flushing, and log compression.
- Handles automatic retained snapshots from `retain` config.

Important behavior:
- Mutations run under `fs->mutlk` and epochs; readers enter epochs without the mutation lock.
- `sync()` performs ordered passes: update snapshots/deadlists/logs, write arena headers, write superblocks, write arena footers, then free old deadlist data.
- Writes allocate new data blocks and then upsert `Kdat` records plus an `Owstat` metadata update.
- Truncation and `ORCLOSE` are deferred as admin messages so block-clearing can run outside the foreground request path.
- Dump attach exposes snapshot labels as a synthetic readonly directory.
- Auth uses factotum `p9any` unless auth is disabled.

Notable risks:
- Many routines depend on precise lock/epoch ordering; `truncwait()` explicitly drops and reacquires mutation state to avoid blocking the sweeper.
- Readonly transition is used as a safety latch after serious sync or mutation failures.
- Some error comments note intentional leaks on exceptional paths to avoid compounding corruption.
