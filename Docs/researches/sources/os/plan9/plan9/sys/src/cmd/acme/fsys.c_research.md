# File Research: sources/os/plan9/plan9/sys/src/cmd/acme/fsys.c

This file implements Acme’s 9P filesystem front end.

Key behavior:
- Defines global and per-window directory tables for `/mnt/acme`.
- `fsysinit()` creates a pipe-backed 9P service and starts `fsysproc()`.
- `fsysproc()` reads 9P messages, decodes them, allocates `Xfid`s, dispatches by fcall type, and delegates opened-file operations to xfid workers.
- `fsysmount()` mounts the service into a child namespace and binds it over `/mnt/wsys` and before `/dev`.
- `fsyswalk()` supports root, numeric window directories, `new`, global files, and per-window files.
- `fsysread()` serves directory listings and delegates normal file reads.
- `fsysopen()`, `fsysclunk()`, `fsysstat()`, and others enforce permissions and lifecycle.
- `Mntdir` refcount helpers manage per-command mount identity, working directory, and include paths.

Important details:
- `messagesize` is negotiated by `Tversion`.
- Attach checks `uname` against `/dev/user`.
- Walking `new` asks GUI thread to create a window via `cnewwindow`.
- Root directory listing includes sorted numeric window ids.
- Create/remove/wstat/auth are denied.

Filesystem relevance:
- Primary Acme pseudo-filesystem implementation; exposes editor state and control surfaces as 9P files.
