
# sources/distributed-fs/xrootd/src/XrdHttp/XrdHttpReq.cc

## Purpose

`XrdHttpReq.cc` implements the logical HTTP/WebDAV request handler sitting behind `XrdHttpProtocol`. It parses request lines and headers, maps HTTP methods to XRootD bridge operations, handles GET/HEAD/PUT/DELETE/PROPFIND/MKCOL/MOVE/OPTIONS behavior, formats responses, processes bridge callbacks, manages range reads and chunked transfers, constructs redirects and opaque credentials, and resets per-request state for keepalive reuse.

## Important APIs, Types, And Functions

- Parsing helpers: `parseFirstLine()`, `parseLine()`, `parseHost()`, `parseScitag()`, `parseResource()`, `sanitizeResourcePfx()`, `addCgi()`, `parseBody()`, `trim()`, and `ISOdatetime()`.
- Bridge callback methods inherited from `XrdXrootd::Bridge::Result`: `Data()`, `File()`, `Done()`, `Error()`, and `Redir()`.
- Request execution: `ProcessHTTPReq()` is the main method-specific state machine.
- Response post-processing: `PostProcessHTTPReq()`, `PostProcessChecksum()`, `PostProcessListing()`, `ReturnGetHeaders()`, and `sendFooterError()`.
- Range and read helpers: `ReqReadV()`, `clientMarshallReadAheadList()`, `clientUnMarshallReadAheadList()`, `buildPartialHdr()`, `buildPartialHdrEnd()`, `getfhandle()`, `getReadResponse()`, `sendReadResponseSingleRange()`, and `sendReadResponsesMultiRanges()`.
- Header helpers: `prepareChecksumQuery()`, `setTransferStatusHeader()`, `addAgeHeader()`, and `addETagHeader()`.
- Security/redirect helper: `appendOpaque()` carries existing opaque parameters and optionally signed HTTP token fields into redirect URLs.
- `reset()` clears request-local state, read range state, digest state, bridge state, body counters, headers, opaque environment, monitoring state, and timing.

## Control Flow

`XrdHttpProtocol::Process()` feeds the first line to `parseFirstLine()` and each header to `parseLine()`. The first line selects `ReqType` and resource. Header parsing records all headers for plugins, handles keepalive, host, Range, validated Content-Length, Destination, digest preference headers, WebDAV depth, `Expect: 100-continue`, trailer support, validated `Transfer-Encoding: chunked`, `X-Transfer-Status`, packet marking `scitag`, user-agent, Origin for CORS, and configured header-to-CGI mappings.

Before method dispatch, `ProcessHTTPReq()` appends `oss.asize` for PUTs with known length and appends configured header-to-CGI opaque parameters once. At `reqstate == 0`, external handlers get first chance through `FindMatchingExtHandler()`.

For `GET`, the request state machine opens the file with `kXR_open` and `kXR_retstat`, optionally performs a checksum query for Want-Digest/Want-Repr-Digest, closes directory handles, performs directory listing, sends GET response headers once, then repeatedly issues `kXR_read` or `kXR_readv` using `XrdHttpReadRangeHandler::NextReadList()`. Completion closes the file. Static `/static/` resources can be served from embedded constants, redirected, or served from preloaded memory.

For `HEAD`, the code stats the path, optionally runs a checksum query, and sends headers without a body. For `PUT`, it opens for write, optionally sends `100 Continue`, then writes fixed-length body bytes or parses chunked request framing and writes each chunk until close, finally sending `201`. `DELETE` stats first to choose `kXR_rmdir` or `kXR_rm`. `PROPFIND` reads an optional small XML body, stats the target, and optionally dirlists depth-one children into a WebDAV multistatus response. `MKCOL` maps to `kXR_mkdir`; `MOVE` validates destination host for manager role and maps to `kXR_mv`; `OPTIONS` returns DAV/Allow headers; `PATCH` and unsupported methods return 501.

Bridge callbacks store response fields and call `PostProcessHTTPReq()`. The post-processor interprets current method and `reqstate`, parses stat strings, extracts file handles, builds checksums and listings, advances read/write counters, sends errors or success responses, and returns `0`, `1`, or `-1` to indicate more bridge work, completion, or connection failure.

## State And Persistence

State is per request object and reset between keepalive requests. Major fields include parsed headers, resource and opaque parameters, request type, body length, keepalive, depth, file handle, file size/flags/modtime/etag, bridge request/response state, I/O vectors valid only during callbacks, string response accumulator, written byte count, digest request/cache state, range handler, chunked-transfer offsets, trailer flags, packet marking scitag, monitoring state, and start time. There is no durable persistence; `resourceplusopaque` is mutated during processing to include internal query parameters.

## Dependencies And Integration Points

This file depends on `XrdHttpReq.hh`, `XrdHttpProtocol.hh`, `XrdHttpTrace.hh`, `XrdHttpExtHandler.hh`, `XrdHttpHeaderUtils`, `XrdHttpUtils`, `XrdHttpStatic`, XRootD bridge/protocol types, packet marking, checksum handler, read range handler, and utility encoding/hash functions. It is tightly coupled to `XrdHttpProtocol` via friend access for bridge, link, buffer, response, config, CORS/static behavior, and security state. It integrates with monitoring through `monState`, `startTime`, and response helper calls in `XrdHttpProtocol`.

## Risks And Edge Cases

- Request parsing is mostly in-place C string manipulation; malformed lines, long tokens, and missing CRLFs are rejected, but maintainers must preserve bounds checks.
- `parseLine()` stores `allheaders[key]` with original header casing; later lookup for header-to-CGI is case-insensitive by iterating config mappings.
- `parseResource()` strips `http://` and `https://` prefixes and collapses double slashes, which is protective but may alter unusual valid paths.
- `appendOpaque()` always appends `?`; URLs already containing query strings rely on prior redirection context to avoid malformed separators.
- PUT chunked parser intentionally ignores trailer headers and caps chunk-size line length, but chunk extensions are only lightly parsed.
- Range handling depends on ordered bridge responses and correct short-read behavior.
- Multipart responses use hardcoded boundary `123456`, which could theoretically collide with payload content.
- Directory listing and PROPFIND build XML/HTML strings in memory; very large listings may grow `stringresp`.
- Several responses pass body length `0` with non-null bodies, relying on `SendSimpleResp()` to calculate length.
- Once a GET body has started, non-trailer clients cannot receive a normal HTTP error; `sendFooterError()` can only return failure unless `X-Transfer-Status` trailers were negotiated.
- `reset()` calls `memset(&xrdresp, 0, sizeof(xrdresp))` after assigning response enums; this is probably harmless for scalar enum storage but visually confusing.
- Security-sensitive header parsing for Content-Length and Transfer-Encoding has explicit smuggling defenses; regressions here are high risk.

## Test Signals

Tests should cover request-line parsing for all methods, invalid leading space, unknown methods, resource decoding/sanitization, duplicate and conflicting Content-Length, `Transfer-Encoding` validation, CL+TE rejection in both orders, Range parsing integration, `Expect: 100-continue`, scitag CGI injection, header2cgi opaque append, Want-Digest and Want-Repr-Digest selection, GET full/single/multi-range headers, 416 behavior, read/readv response formatting, chunked response trailers, PUT fixed-length and chunked uploads, static file serving/redirect/preload, directory GET listing, PROPFIND depth 0/1 XML, DELETE file versus directory, MOVE host enforcement, redirect host CRLF rejection, opaque credential propagation, keepalive reset, and monitoring state reset.
