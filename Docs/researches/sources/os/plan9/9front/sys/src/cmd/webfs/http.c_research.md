# File Research: sources/os/plan9/9front/sys/src/cmd/webfs/http.c

HTTP/HTTPS transport, connection pooling, authentication, proxy, cookie, redirect, chunking, and body streaming implementation for `webfs`.

Key behavior:
- `hdial()` opens direct or proxy TCP connections, wraps TLS for HTTPS endpoints or HTTPS proxies, and marks HTTPS-through-proxy connections as tunnels.
- `hclose()` returns reusable keep-alive connections to a bounded idle pool, enforces per-peer and total limits, and starts a reaper process for idle connections.
- `hread()`, `hwrite()`, and `hline()` provide buffered body reads, complete writes, and line/header reads with continuation folding.
- Basic and Digest authentication are supported through Plan 9 auth mechanisms and cached by URL scope in `hauth`; digest cache entries are flushed after one use.
- `flushauth()` removes cached credentials matching URL and/or auth string.
- `http()` forks a worker process, prepares request headers, optionally spools POST bodies to a temp file for retries/content-length calculation, sends request headers/body, receives status/headers, handles redirects, 401/407 auth, proxy CONNECT, 411 retry with length, chunked bodies, and no-body statuses.
- Response headers and final URL metadata are attached to `qbody` or `qerror`; error status closes `qbody` with status text and streams the response into `qerror` until success/error routing is decided.
- Integrates with `/mnt/webcookies/http` by writing request URL to fetch cookies and later writing `Set-Cookie` headers back.

Notable dependencies:
- Plan 9 networking, TLS (`tlsClient`), auth, libsec encoding, libthread, and the local `Buq`, `Url`, and `Key` helpers.

Research notes:
- Worker retries are bounded to 12 attempts.
- For unknown-length non-chunked bodies, keep-alive is disabled because EOF delimits the body.
- Posting uses a helper process sharing memory with the worker; `h->cancel` stops it on retry/error.
