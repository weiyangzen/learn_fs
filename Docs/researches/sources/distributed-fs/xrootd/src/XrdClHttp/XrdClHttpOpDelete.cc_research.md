# sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpOpDelete.cc

## Purpose
`XrdClHttpOpDelete.cc` implements `CurlDeleteOp`, the HTTP DELETE operation used by filesystem removal calls.

## Important APIs and Functions
The constructor forwards handler, URL, timeout, logger, response-info flag, connection callout, and header callout to `CurlOperation`. `Setup` calls the base setup then sets `CURLOPT_CUSTOMREQUEST` to `"DELETE"`. `ReleaseHandle` clears the custom request. `Success` returns an OK status and optionally a `DeleteResponseInfo`.

## Control Flow
`Filesystem::Rm` and `RmDir` enqueue this operation. Once curl completes successfully, `Success` marks the operation done without failure and invokes the original response handler.

## State and Persistence
The remote target is deleted. The only additional in-memory state is the response-info opt-in flag.

## Dependencies and Integration Points
The file depends on `XrdClHttpOps.hh`, `XrdClHttpResponses.hh`, and XrdCl logging. It relies on base `CurlOperation` for HTTP status-to-XRootD error mapping.

## Risks and Test Signals
Tests should cover successful delete with and without response info, HTTP 404/403 mapping through base failure logic, queue submission from filesystem methods, and handle reuse after custom request reset.
