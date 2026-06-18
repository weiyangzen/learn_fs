# File Research: sources/os/plan9/plan9/sys/src/cmd/webfs/plumb.c

This file integrates `webfs` with Plan 9 plumbing.

Initialization:
- `plumbinit` opens `send` for writing and `web` for reading.
- `plumbstart` creates a channel and starts:
  - `plumbwebproc`: receives messages from plumb port `web`.
  - `plumbwebthread`: converts plumb messages into `plumburl` calls.

Incoming plumbing:
- Uses `baseurl` attribute if present, else message working directory as base.
- `plumburl` creates a plumbed web client and opens/replumbs it asynchronously.

Outgoing/replumbing:
- `replumb(Client*)` creates a plumb message for a fetched body.
- Adds `url` and optional `content-type` attributes.
- Maps known MIME types to extensions; otherwise guesses from URL suffix or defaults to `txt`.
- Sets `c->ext` and sends `/mnt/web/<num>/body.<ext>` as message data.
- Sends in a separate proc to avoid deadlock.

Notable behavior:
- `addattr` stores raw name/value pointers without duplicating strings; `freeattrs` frees only attribute nodes, not pointed-to strings.
