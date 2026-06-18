# File Research: sources/os/plan9/9front/sys/src/cmd/webfs/fs.c

9p filesystem front end for HTTP requests. It exposes cloneable clients with control files, request/response body streams, parsed URL fields, response headers, and error bodies.

Key behavior:
- Root contains `ctl`, `clone`, and numbered client directories.
- Opening `clone` allocates a `Client` and turns the fid into that client's `ctl`.
- Client directories expose `ctl`, `body`, `postbody`, `errorbody`, `parsed`, and dynamic header files; `parsed` exposes URL, scheme, user, password, host, port, path, query, and fragment.
- `ctl` messages set URL, base URL, request method, bulk headers, `User-Agent`, and `Content-Type`; root `ctl` sets user agent, timeout, auth flushing, and preauthentication.
- Opening `body` starts a GET or custom request; opening `postbody` starts a POST-like request with a writable request body queue; `errorbody` reads response/error payloads.
- Default request headers include `Accept: */*`, `Connection: keep-alive`, and configured `User-Agent` unless supplied.
- `fswalk1()`, `fsmkdir()`, and generator callbacks build stable qids and directory listings from client state, parsed URL state, and response headers.
- `fsdestroyfid()` closes queues, marks body streams closed, releases client references, and frees copied header keys.
- `main()` installs URL/header formatters, reads `httpproxy`, sets defaults, and mounts at `/mnt/web` or a supplied mount/service.

Notable dependencies:
- Plan 9 lib9p service callbacks.
- `Buq` stream queues from `buq.c`, URL helpers from `url.c`, HTTP worker from `http.c`, and cookie service at `/mnt/webcookies/http`.

Research notes:
- `Client` objects are a fixed array of 256 entries reused by reference count.
- Header files copy the header key/value because queue-owned response headers may disappear.
- After a request starts, `cl->url` and `cl->hdr` ownership moves to the HTTP worker path.
