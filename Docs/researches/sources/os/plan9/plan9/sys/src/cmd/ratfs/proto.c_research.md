# File Research: sources/os/plan9/plan9/sys/src/cmd/ratfs/proto.c

9P protocol implementation for ratfs.

Main dispatch:
- `io()` reads 9P messages from `srvfd`, decodes with `convM2S()`, dispatches by message type, and logs debug traffic.
- `reply()` converts successful replies by incrementing type, or emits `Rerror`.
- `newfid()` allocates/reuses `Fid` records.

Implemented 9P operations:
- `rversion()` clamps msize to `MAXRPC`.
- `rauth()` rejects auth as unnecessary.
- `rattach()` reloads config/control files when mtimes change, cleans temporary trusted entries, and binds fid to root.
- `rwalk()` supports clone-walk and partial walk semantics.
- `ropen()` permits writable access only to `ctl`, read-only elsewhere.
- `rcreate()` allows creates only where directory permissions allow, practically the `trusted` directory, creating temporary trusted CIDR files.
- `rread()` supports directory reads for real directories and address directories; non-directories return EOF.
- `rwrite()` accepts `ctl` commands: `reload`, `debug`, `nodebug`.
- `rclunk()` releases fid state.
- `rremove()` removes only owner-owned temporary trusted files.
- `rstat()` serializes node metadata, adjusting `dummy` name for address pseudo-files.
- `rwstat()` is unimplemented.

Risk/notes:
- Permission checking is deliberately simplified because most files are read-only or ctl-only.
- `rwrite()` NUL-terminates data using the extra byte in `rbuf`.
- Temporary trusted qids wrap before colliding with address-file qids.
