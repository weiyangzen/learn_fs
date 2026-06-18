# File Research: sources/os/plan9/9front/sys/src/cmd/acme/fsys.c

This file implements the front dispatcher for Acme's synthetic 9P filesystem.

Key responsibilities:
- Defines global and per-window directory tables:
  - Global: `.`, `acme`, `cons`, `consctl`, `draw`, `editout`, `index`, `label`, `log`, `new`.
  - Window: `.`, `addr`, `body`, `ctl`, `data`, `editout`, `errors`, `event`, `rdsel`, `wrsel`, `tag`, `xdata`.
- `fsysinit()` creates the server pipe, installs 9P formatting, opens `/dev/time`, sets `user`, and starts `fsysproc()`.
- `fsysproc()` reads 9P messages, allocates/reuses `Xfid` workers, decodes `Fcall`s, validates fids, and dispatches by request type.
- `fsysaddid()`, `fsysincid()`, and `fsysdelid()` manage per-mounted-command `Mntdir` records and include directories.
- `fsysmount()` mounts Acme's server on `/mnt/acme`, binds `/mnt/wsys`, and binds Acme before `/dev` for child commands.
- `fsysclose()` closes server endpoints.
- `respond()` serializes replies or errors.
- Implements core 9P operations:
  - `version`, `auth`, `flush`, `attach`, `walk`, `open`, `create`, `read`, `write`, `clunk`, `remove`, `stat`, `wstat`.
- `fsyswalk()` resolves numeric window directories, `new` window creation, global names, and per-window names.
- `fsysread()` handles directory listing and delegates file reads to xfid workers.
- `newfid()` manages a small hash table of fids.
- `dostat()` synthesizes `Dir` metadata.

Important dependencies:
- Delegates actual file open/read/write/close behavior to `xfid*` functions implemented elsewhere.
- Uses row/column/window state to enumerate windows and resolve IDs.
- Uses Qid encoding macros from `dat.h`.

Filesystem/storage relevance:
- This is the primary Acme-as-filesystem implementation. It exposes editor state as a 9P namespace and lets programs control windows via file operations.

Notes:
- `create`, `remove`, and `wstat` are denied.
- `walk` to `new` creates a new Acme window through `newwindowthread()` because graphics work must happen outside the server process context.
