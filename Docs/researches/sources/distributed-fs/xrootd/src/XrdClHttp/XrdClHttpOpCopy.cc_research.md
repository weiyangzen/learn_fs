# sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpOpCopy.cc

## Purpose
`XrdClHttpOpCopy.cc` implements `CurlCopyOp`, an HTTP third-party-copy operation using the `COPY` verb and a text control channel for performance/failure markers.

## Important APIs and Functions
The constructor accepts source URL/headers, destination URL/headers, timeout, logger, and connection callout. It prefixes source headers with `TransferHeader`, stores destination headers normally, and lowers the minimum rate. `Setup` installs write callback/data, sets `CUSTOMREQUEST` to `COPY`, and adds the `Source` header. `WriteCallback` splits response text into lines and calls `HandleLine`. `HandleLine` parses `"Perf Marker"`, `"End"`, `"Stripe Bytes Transferred"`, `"success"`, and `"failure"` markers.

## Control Flow
During transfer, response body lines update byte-mark progress and optional callback notifications. Success currently reports a generic OK response to the handler. `ReleaseHandle` clears curl callbacks, custom request, headers, and transfer info callback.

## State and Persistence
Remote state is changed at the destination endpoint by the COPY request. In-memory state tracks source URL, partial line buffer, progress callback, latest byte marker, success marker flag, and failure text.

## Dependencies and Integration Points
The operation derives from `CurlOperation` and uses `ltrim_view` from HTTP utilities. It is declared in `XrdClHttpOps.hh`; instantiation likely occurs outside the listed files.

## Risks and Test Signals
The parsed `m_sent_success` and `m_failure` fields are not used in `Success`, so control-channel failures may not affect final status unless handled in omitted base code. Tests should cover fragmented response lines, malformed numeric markers, progress callback invocation, remote failure marker handling, and cleanup of curl handle options.
