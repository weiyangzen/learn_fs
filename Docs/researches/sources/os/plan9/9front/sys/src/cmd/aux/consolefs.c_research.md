# File Research: sources/os/plan9/9front/sys/src/cmd/aux/consolefs.c

Role: Custom user-space 9P filesystem exposing configured serial consoles under a one-level tree.

Filesystem model:
- Top directory contains up to three files per console: `<name>`, `<name>ctl`, and `<name>stat`.
- Console definitions come from an ndb database, default `/lib/ndb/consoledb`, with attributes such as `console`, `dev`, `speed`, `cronly`, and `openondemand`.
- Mount point defaults to `/mnt/consoles`; it also posts `/srv/consoles` when needed.

Implementation architecture:
- Implements raw 9P message handling directly with `read9pmsg`, `convM2S`, and `convS2M`, rather than lib9p.
- `Fs` owns fid hash tables and console list; `Console` owns device/control/status fds and list of active data fids; `Fid` owns per-reader circular buffers and delayed read request list.
- `fsrun` reloads the ndb database when mtime changes, dispatches requests through `fcall[]`, and maintains fid references manually.

Console behavior:
- `fsreader` reads from each console device and broadcasts data into every open data fid ring buffer.
- Reads from console data files may block by queuing the request until `fskick` has buffered data.
- Writes to console data files go to the real device unless the console is `/dev/null`, in which case chat-mode broadcasts user-prefixed lines to listeners.
- `ctl` writes are forwarded to the device control file; `stat` reads are served from the device stat file.

Access control:
- `userok` checks console-specific `uid` and `gid` records in the ndb database; `ingroup` resolves group membership from ndb.

Notable details:
- Per-fid circular buffers preserve recent tail data and may drop old bytes if writers overtake readers.
- `openondemand` consoles are opened only while clients are attached.
