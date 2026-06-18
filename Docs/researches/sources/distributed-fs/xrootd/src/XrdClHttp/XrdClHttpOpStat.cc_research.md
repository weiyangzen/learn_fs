# sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpOpStat.cc

## Purpose

This file implements `CurlStatOp`, the HTTP stat/open metadata operation. It can use either `HEAD` or WebDAV `PROPFIND` depending on endpoint capabilities cached from `OPTIONS`, parses object size and directory state, and returns either plain XRootD stat/open responses or extended response-info wrappers.

## Important APIs, types, and functions

`Setup` installs the write callback and chooses `HEAD` or `PROPFIND` using `VerbsCache`. `RequiresOptions` asks the worker to probe endpoints whose allowed verbs are unset. `OptionsDone` reconfigures the in-flight handle after a successful OPTIONS result. `Redirect` preserves headers while redirecting, then decides whether the redirected endpoint needs another OPTIONS lookup. `WriteCallback` stores PROPFIND XML bodies up to 1 MB. `GetStatInfo`, `ParseProp`, and `SuccessImpl` convert HTTP/WebDAV metadata into XRootD response objects.

`Success` calls `SuccessImpl(true)`, while `CurlOpenOp` reuses `SuccessImpl(false)` to avoid returning a stat object when open metadata is only used internally.

## Control flow

For cached PROPFIND support, setup sends `PROPFIND` with `Depth: 0` and enables a body callback; otherwise it sends `HEAD` with `CURLOPT_NOBODY`. If no capability is cached, the worker runs `CurlOptionsOp` first, then calls `OptionsDone` and executes the parent stat operation. On redirect, the operation resets the target through `CurlOperation::Redirect`; if the target has unknown verb support, the worker reinvokes OPTIONS before restarting.

On success, `GetStatInfo` reads `Content-Length` for `HEAD` or parses a WebDAV `D:multistatus/D:response/D:propstat/D:prop` XML body for `getcontentlength` and `resourcetype`. Directories may omit length and are reported as size zero. `SuccessImpl` emits `StatInfo`/`StatResponse` or `OpenResponseInfo` and moves accumulated `ResponseInfo` when requested.

## State and persistence behavior

The only persistent state is indirect: discovered PROPFIND support is stored in the global `VerbsCache`. Per-operation state tracks whether PROPFIND is active, buffered XML, directory flag, parsed length, and the response-info option. `ReleaseHandle` resets curl options so handles can be recycled safely.

## Dependencies and integration points

The implementation depends on TinyXML, `VerbsCache`, `HeaderParser`, `CurlWorker` OPTIONS chaining, and `XrdClHttpResponses.hh` wrappers. It is used by file open/stat, filesystem stat, checksum inheritance, and query operations that derive from `CurlStatOp`.

## Risks and edge cases

PROPFIND response parsing assumes `D:` or `lp1:` prefixed element names and can reject namespace-equivalent XML using different prefixes. `std::stoll` exceptions from bad content length are not caught in `ParseProp`, so malformed XML values could throw through the worker. The cache key is endpoint-level, not path-level, so mixed endpoint behavior can cause suboptimal verb choice. Redirects require careful restoration of pre-redirect headers when an OPTIONS probe must be inserted.

## Test signals

Important tests should exercise HEAD size extraction, PROPFIND directory/file parsing, 1 MB XML body cap, missing size failure for non-directory objects, capability cache miss/hit paths, redirect-to-unknown-endpoint OPTIONS reinvocation, and extended response-info object creation. No dedicated stat tests were found in the checkout.
