# File Research: sources/os/plan9/plan9/sys/src/cmd/replica/applylog.c

Read status: complete, 1235 lines.

`replica/applylog` applies a stream of replica log entries to a local tree and updates the client database. It is the most complex replica file in this group, implementing add/delete/content-change/metadata-change handling, conflict detection, forced conflict resolution, safe copying, and incremental time tracking.

The input log format is tokenized into timestamp, sequence number, operation verb, path, remote name, mode, uid, gid, mtime, and length. `main` checks each entry against the local database, local filesystem, remote filesystem, match filters, and `-s`/`-c` resolution overrides.

For `d`, it removes local files if they were not locally changed or if the resolution policy allows it. For `a`, it creates directories or copies remote files. For `c`, it updates file contents when local contents are not conflicting. For `m`, it updates metadata when local content or metadata does not conflict or is overridden.

Copying is deliberately cautious. `copytotemp` spools remote contents to a temp file and re-stats the remote file to detect changes underfoot. `copy1` uses up to `Nwork` workers with `pread`/`pwrite` offsets. `copyfile` includes a safe-install path that renames existing `bin/*` targets to `_target` before overwrite.

The `copyerr` in-memory database records transient missing/copy errors. `samecontents` compares local and remote content through a temp-spooled remote copy. `timefile` support tracks last applied log time/sequence and stops advancing when skipped changes could make later state unsafe.

`membogus` copies and re-execs `applylog` from `/tmp` to avoid overwriting itself during updates.

Filesystem relevance: central replica application engine for local filesystem mutation, remote file reads, metadata writes, conflict policy, and safe installation.
