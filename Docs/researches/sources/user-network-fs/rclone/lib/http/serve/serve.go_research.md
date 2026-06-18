# sources/user-network-fs/rclone/lib/http/serve/serve.go

Source read signal: reviewed complete local file (115 lines, sha256 4f51d0736512c95b).

Purpose: Serves an `fs.Object` over HTTP for GET and HEAD, including range requests and selected metadata headers.

Important APIs/types/functions: Exported `Object(w, r, o)` is the main API.

Control flow: Rejects non-GET/HEAD, sets range/content-length/content-type/last-modified headers, forwards selected metadata headers, returns immediately for HEAD, parses Range into open options for GET, opens the object, wraps it in accounting, writes the status, and streams with `io.Copy`.

State and persistence behavior: Does not mutate the object; creates accounting transfer state for the request. Response headers/body are the only output.

Dependencies and integration points: Uses `fs.Object`, `fs.MimeType`, `fs.GetMetadata`, `fs.ParseRangeOption`, and `accounting.Stats`. Integrated by serve frontends that map URLs to objects.

Risks and test signals: Range math must avoid invalid content ranges and preserve correct content length. Errors after headers are written can only be logged. Metadata header pass-through affects browser/cache behavior.
