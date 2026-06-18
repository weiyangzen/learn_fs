# sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpOpOptions.cc

## Purpose
`XrdClHttpOpOptions.cc` implements `CurlOptionsOp`, an advisory OPTIONS request used to discover allowed HTTP/WebDAV verbs and cache them for redirect and operation decisions.

## Important APIs and Functions
`Setup` configures the curl handle for `OPTIONS` and no response body. `Success` writes parsed allowed verbs into `VerbsCache`. `Fail` records unknown verbs in the cache but otherwise ignores failure so the parent operation can continue. `ReleaseHandle` clears custom request and `CURLOPT_NOBODY`.

## Control Flow
The worker inserts this operation when a parent operation requires verb discovery. On success or failure, the cache is updated and worker logic resumes the parent operation.

## State and Persistence
State is cached in the process-wide `VerbsCache`; no remote state changes occur.

## Dependencies and Integration Points
It depends on `CurlOperation`, `VerbsCache`, and header parsing for allowed verbs. Worker logic in HTTP utilities recognizes `CurlOptionsOp` and reactivates parent operations.

## Risks and Test Signals
OPTIONS failure is intentionally non-fatal, so tests should verify parent continuation on 405 or network failure, correct cache entries for allowed verbs, no-body setup cleanup, and redirect paths that require a second OPTIONS lookup.
