# sources/sync-backup/git-lfs/lfshttp/verbose.go

Purpose: Implements HTTP trace output for requests and responses, including body tracing for textual content and redaction of Basic auth by default.

Important APIs/types/functions: `traceRequest`, `tracedRequest`, `traceResponse`, `tracedResponse`, `tracedRead`, `traceHTTPDump`, `isTraceableContent`, and `traceReq`.

Control flow: `traceRequest` logs method/URL, optionally dumps request headers, validates body seekability, rewinds body, and wraps it for size accounting and optional textual output. `traceResponse` logs status, wraps body to trace reads and stats, and optionally dumps response headers. `traceHTTPDump` prefixes lines and redacts Basic Authorization unless debugging verbose is enabled.

State and persistence behavior: Mutates `req.Body` and `res.Body` wrappers in memory. Writes verbose output to `VerboseOut` and tracer logs. Response stats emit on EOF.

Dependencies and integration points: Works with `lfshttp.Client.DoWithRedirect`, `stats.go`, `httputil.Dump*`, and `tracerx`.

Risks and edge cases: Request bodies must implement `ReadSeekCloser`; non-seekable non-nil bodies return an error. Binary content bodies are not printed, but headers still are. Redaction is specific to Basic authorization lines.

Test signals: `verbose_test.go` covers verbose text output, binary body suppression, redaction, debugging mode unredaction, and disabled output.
