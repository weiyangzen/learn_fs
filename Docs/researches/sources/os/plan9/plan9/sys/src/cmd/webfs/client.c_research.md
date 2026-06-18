# File Research: sources/os/plan9/plan9/sys/src/cmd/webfs/client.c

This file manages `webfs` client slots, per-client worker threads, control-file parsing, redirects, authentication retries, and plumbed URL handling.

Client lifecycle:
- `newclient` reuses a zero-ref slot or allocates a new `Client`, request channel, worker thread, I/O proc, copied global controls, and client number.
- `closeclient` decrements `ref`; when it reaches zero, it closes open body transport, frees content type, post body, URL, redirect/auth strings, and resets body state.
- `clonectl` deep-copies string fields in `Ctl`.

Body open/read:
- `clientbodyopen` follows redirects up to `redirectlimit`, calls the URL scheme's `open`, retries once for authentication, parses redirected URLs relative to current URL, and responds to pending open request.
- `clientbodyread` delegates to URL scheme `read` and responds.
- `clientthread` receives 9P requests over `creq`; for plumbed clients it opens immediately and replumbs a generated body path.

Plumbing:
- `plumburl` parses optional base URL and target URL, creates a plumbed client, holds a reference, and nudges its worker.

Control commands:
- Tables define global and per-client controls:
  - `acceptcookies`, `sendcookies`, `redirectlimit`, `useragent`.
  - Global debug knobs: `chatty9p`, `fsdebug`, `cookiedebug`, `urldebug`, `httpdebug`.
  - Client URL setters: `baseurl`, `url`.
- `parseas` applies bool, string, URL, and integer values.
- `ctlwrite`, `clientctlwrite`, and `globalctlwrite` dispatch commands.
- `ctlread` and `globalctlread` render current settings.

Notable risks:
- URL control writes replace existing `Url*` immediately after parsing, but no explicit synchronization with active body I/O beyond normal 9P sequencing.
- Authentication retry only permits one retry via `nauth++ < 1`.
