# File Research: sources/os/plan9/9front/sys/src/cmd/ratfs/proto.c

This file implements the ratfs 9P protocol loop and request handlers.

Key responsibilities:
- `io()` reads 9P messages from `srvfd`, decodes them, dispatches through `fcalls[]`, and writes replies.
- `reply()` converts successful replies or `Rerror` responses back to the client.
- `newfid()` allocates/reuses fid records.
- Implements handlers for version, flush, auth, attach, clone/walk, open, create, read, write, clunk, remove, stat, and wstat.

Protocol behavior:
- Authentication is not required.
- `rattach()` reloads config/control files when mtimes change and cleans expired trusted entries.
- `rwalk()` supports clone-walk semantics and partial walk responses.
- `ropen()` allows only write access to `ctl`; all other files/directories are read-only.
- `rcreate()` only creates temporary trusted CIDR files in writable trusted directories.
- `rread()` only returns directory contents; non-directories read as EOF.
- `rwrite()` accepts `ctl` commands: `reload`, `debug [file]`, and `nodebug`.
- `rremove()` only removes temporary trusted files owned by the calling user.
- `rwstat()` is intentionally unimplemented.

Implementation notes:
- Permission checks rely on atomized uid/gid pointer equality.
- `rbuf` is sized with one spare byte so `rwrite()` can NUL-terminate command text.
