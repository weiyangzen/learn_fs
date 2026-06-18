# sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpOpChecksum.cc

## Purpose
`XrdClHttpOpChecksum.cc` implements `CurlChecksumOp`, a checksum query operation that issues an HTTP HEAD with `Want-Digest` and returns an XrdCl query buffer containing the selected digest.

## Important APIs and Functions
The constructor derives from `CurlStatOp` and stores the preferred checksum type. `OptionsDone` intentionally does nothing so the parent stat operation does not switch to PROPFIND. `Setup` calls `CurlStatOp::Setup`, forces HEAD semantics (`CURLOPT_NOBODY`, no custom request), and adds `Want-Digest`. `Redirect` reapplies HEAD settings. `ReleaseHandle` clears HTTP headers. `Success` selects and hex-encodes the preferred or first available checksum.

## Control Flow
On success, parsed response headers are queried for checksums. If the preferred checksum exists, it is used; otherwise the first available checksum is used. Missing checksums produce `errCheckSumError`. Successful responses are formatted as `"type hex"` in a `QueryResponse` and may carry `ResponseInfo`.

## State and Persistence
The operation stores only the preferred checksum plus inherited curl/header state. It does not mutate remote state.

## Dependencies and Integration Points
It depends on `CurlStatOp`, `HeaderParser::ChecksumTypeToDigestName`, `ChecksumInfo`, `QueryResponse`, XrdCl buffers, and response-info plumbing. `Filesystem::Query(Checksum)` instantiates it.

## Risks and Test Signals
Checksum byte ordering and hex formatting are critical. Tests should cover preferred present, fallback present, none present, redirects retaining HEAD mode, unknown checksum request fallback in filesystem code, and handle reuse after `ReleaseHandle`.
