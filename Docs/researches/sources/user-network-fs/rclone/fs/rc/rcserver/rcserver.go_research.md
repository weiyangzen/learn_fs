# sources/user-network-fs/rclone/fs/rc/rcserver/rcserver.go

## Purpose
This file implements the main HTTP remote-control server, including RC POST dispatch, local/WebGUI file serving, remote file serving, metrics routing, pprof routing, auth gating, and server lifecycle.

## Important APIs, Types, and Functions
- `Start(ctx, opt)` starts the RC server only when enabled.
- `Server` holds context, `libhttp.Server`, static file/plugin handlers, options, and a startup snapshot of `NoAuth`.
- `newServer` prepares MIME types, WebGUI/static handlers, default WebGUI credentials, `libhttp.Server`, middleware, pprof, and route handlers.
- `handler`, `handlePost`, `handleGet`, and `handleOptions` implement request dispatch.
- `checkServeRemote` enforces security rules before instantiating remotes from request paths.
- `serveRemote` and `serveRoot` implement remote object/directory browsing.
- `Serve`, `URLs`, `Wait`, and `Shutdown` manage lifecycle.

## Control Flow
POST requests parse URL/form/JSON input into `rc.Params`, honor `Prefer: respond-async` by setting `_async`, look up `rc.Calls`, enforce auth unless the call is `NoAuth` or `--rc-no-auth` was set at startup, inject `_request`/`_response` for calls that need them, then execute via `jobs.NewJob` and write JSON. GET/HEAD requests route to remote serving for `/[fs]/path`, `/metrics` when enabled, remote listing, WebGUI plugins, static files, or 404.

## State and Persistence
The server keeps static handler references and a `noAuth` snapshot to prevent runtime option mutation from changing auth semantics. WebGUI mode may download/extract files under the cache directory and mutate auth defaults with generated credentials. Remote serving uses `cache.Get` and may create backend instances.

## Dependencies and Integration Points
It integrates chi middleware through `libhttp.Server`, rclone config/cache/fspath/list/serve packages, RC registry/jobs, WebGUI helpers, pprof on the default mux, and browser opening via `open-golang/open`.

## Risks and Edge Cases
`checkServeRemote` is a key security boundary: unauthenticated servers may serve only configured named remotes, while inline remotes, bare local paths, and connection-string overrides are rejected; `global.*` is rejected even for authenticated requests. POST parsing merges query/form/JSON values with last value wins for repeated query values and JSON overwriting/augmenting the map. RC calls that receive `_response` can write directly, so response ownership must be handled carefully. Browser auto-open embeds basic credentials and a login token in a URL, which should be treated as sensitive.

## Test Signals
`rcserver_test.go` covers static files, range/head requests, remote serving, security rejection for unauthenticated inline/local/global remotes, authenticated serving, RC input parsing, auth/no-auth behavior, async jobs, pprof, directory modtime display, and JSON content type. Metrics route behavior is also covered in `metrics_test.go`.
