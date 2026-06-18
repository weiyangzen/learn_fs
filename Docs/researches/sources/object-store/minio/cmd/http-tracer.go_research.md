# sources/object-store/minio/cmd/http-tracer.go

## Purpose

`http-tracer.go` implements MinIO's server-side HTTP trace middleware. It records request and response metadata, optional bodies, timing, byte counts, source IP, sanitized query strings, and normalized handler names, then publishes `madmin.TraceInfo` events to `globalTrace` subscribers.

## Important APIs, Types, And Control Flow

`redactLDAPPwd` uses `ldapPwdRegex` to replace an `LDAPPassword` query parameter value with a redaction marker while preserving surrounding query content. `getOpName` converts Go function names into stable operation labels such as `s3.*`, `admin.*`, `storageR.*`, `peer.*`, and health names. `httpTracerMiddleware` wraps the response writer with `xhttp.ResponseRecorder`, wraps the request body with `xhttp.RequestRecorder`, installs a `mcontext.TraceCtxt` on the request context, executes the handler, and only builds a trace if subscribers exist for S3 or internal traces.

After the handler returns, the middleware reconstructs request headers including Host and either Content-Length or Transfer-Encoding, computes input bytes from recorded body size plus header lengths, strips default HTTP/HTTPS ports from the node name, chooses `TraceS3` when the traced function starts with `s3.`, and publishes `madmin.TraceInfo` with request, response, and latency/TTFB stats. `httpTrace` is the per-handler wrapper that discovers the handler function name with `runtime.FuncForPC`, enables request and response body logging according to `logBody`, and always logs error bodies. `httpTraceAll` and `httpTraceHdrs` are convenience wrappers for body-inclusive and headers-only tracing.

## State, Dependencies, Integration, Risks, And Tests

State is request-scoped until publication; global state is `globalTrace`, distributed node name flags, and response/request recorder buffers. Dependencies include `madmin-go`, `internal/http`, `internal/handlers`, and `internal/mcontext`. Integration is broad: every HTTP handler that uses `httpTrace*` participates in trace naming and body capture. Risks include sensitive data in logged bodies when `logBody` is true, incomplete query redaction beyond LDAP password, body buffering cost, byte-count approximation by adding header key/value lengths, and traces not emitted if handlers bypass the context wrapper. `http-tracer_test.go` validates LDAP password redaction and indirectly shares the package with HTTP stats race tests.
