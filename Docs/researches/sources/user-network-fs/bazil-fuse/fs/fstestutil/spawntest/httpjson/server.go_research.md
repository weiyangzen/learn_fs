<!-- BEGIN_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/fstestutil/spawntest/httpjson/server.go -->
# sources/user-network-fs/bazil-fuse/fs/fstestutil/spawntest/httpjson/server.go

Purpose: reflection-based adapter from typed Go functions to POST-only JSON HTTP handlers.

Important APIs, types, and functions: exports `ServePOST`; internal `jsonPOST` implements `http.Handler`.

Control flow: `ServePOST` validates function shape `func(context.Context, T) (R, error)`. `ServeHTTP` rejects non-POST, decodes one JSON request with unknown fields disallowed, calls the function with request context, maps returned errors to HTTP 500, marshals the result, and writes JSON.

State and persistence behavior: handler stores reflection values and types only.

Dependencies and integration points: used by spawntest helpers and benchmark control endpoints.

Risks and test signals: reflection panics on bad registration shape; all function errors become 500, so bad-request granularity is absent. Strict JSON is a useful test signal.
<!-- END_FILE_RESEARCH: sources/user-network-fs/bazil-fuse/fs/fstestutil/spawntest/httpjson/server.go -->
