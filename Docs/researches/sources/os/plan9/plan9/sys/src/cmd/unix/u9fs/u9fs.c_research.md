# File Research: sources/os/plan9/plan9/sys/src/cmd/unix/u9fs/u9fs.c

- Role: Main Unix-hosted 9P file server that exports a chrooted Unix filesystem to Plan 9 clients.
- Protocol flow: `serve` reads old/new 9P requests, dispatches to handlers, logs optional `%F` traces, and writes responses; `getfcall` auto-detects 9P1 vs 9P2000.
- Filesystem handlers: Implements version, auth, attach, walk, open, create, read, write, clunk, remove, stat, and wstat by mapping to Unix `stat`, `open`, `pread`, `pwrite`, `mkdir`, `remove`, `rename`, `chmod`, `utime`, `chown`, and `truncate`.
- State: Tracks `Fid` objects with path, stat cache, user, open mode, directory stream, auth flag, and auth magic; tracks users/groups in small hash tables.
- Security model: Auth method selected by `-a`; attaches reject root unless `-u defaultuser` is set; per-request `userchange` switches effective uid and group membership; special files require `aname=device`.
- Filename handling: `enfrog`/`defrog` escape Plan 9-invalid path bytes using backslash hex encoding.
- Risks/notes: Permission checks intentionally rely mostly on effective uid operations but some prechecks are racy. `freefid` closes `fd` only if nonzero, so fd 0 would not close, though file fds are normally opened after stdio/log setup. Wstat is explicitly non-atomic across chmod/utime/chgrp/rename/truncate.
