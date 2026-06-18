# File Research: sources/os/plan9/plan9/sys/src/cmd/fcp.c

Parallel file copy utility.

Key behavior:
- Copies one file to a target file or multiple files into a target directory.
- Rejects directory sources and same-file copies.
- Spawns up to 16 worker processes sharing memory to copy fixed 8 KB chunks with `pread()` and `pwrite()`.
- Preserves mode, mtime, uid, and/or gid depending on `-x`, `-u`, and `-g`.
- On worker failure, posts `failure` notes to other workers.

Important implementation details:
- Shared global `off` is protected by `QLock`; `nextoff()` assigns disjoint chunks to workers.
- Destination is created with source permissions masked to 0777.
- `samefile()` compares qid, dev, and type to avoid self-overwrite.

Risks and invariants:
- The parent waits for all children returned by `wait()`, not only the spawned worker pids.
- Sparse or special file behavior is not explicitly preserved beyond data and selected metadata.
