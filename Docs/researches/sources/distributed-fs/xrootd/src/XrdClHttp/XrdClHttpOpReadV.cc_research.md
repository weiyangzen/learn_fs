# sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpOpReadV.cc

## Purpose

This file implements `XrdClHttp::CurlVectorReadOp`, the HTTP plugin's vector-read operation. It translates an XRootD `ChunkList` into a single HTTP `Range` request containing multiple byte ranges, parses either single-range or `multipart/byteranges` responses, copies returned data into caller-provided buffers, and reports an `XrdCl::VectorReadInfo` to the response handler.

## Important APIs, types, and functions

`CurlVectorReadOp::Setup` installs the libcurl write callback and builds the comma-separated `Range: bytes=start-end,...` header from non-empty chunks. `Fail` adds vector-read offset/length context to errors. `Success` emits any partial final chunk, sets the total size consumed, wraps the `VectorReadInfo` in an `AnyObject`, and invokes the handler. `ReleaseHandle` clears write callback/header/socket options before delegating to `CurlOperation`.

The core parser is `Write`. It handles status `200` as a whole-object response, non-multipart range responses by using `HeaderParser::GetOffset`, and multipart responses by parsing boundary lines and per-part `Content-Range` headers. `CalculateNextBuffer` chooses the requested chunk whose offset best matches the current response part, possibly setting `m_skip_bytes` when the server returns a larger/coalesced range.

State fields inherited from `XrdClHttpOps.hh` include `m_chunk_list`, `m_vr`, `m_current_op`, `m_response_idx`, `m_chunk_buffer_idx`, `m_bytes_consumed`, `m_skip_bytes`, and `m_response_headers`.

## Control flow

The worker calls `Setup`, then libcurl streams body data into `WriteCallback`. `Write` first updates byte statistics, classifies the response shape from parsed headers, then loops through the incoming buffer. If a current response range is active, it skips unwanted bytes, copies useful bytes into the selected `ChunkInfo` buffer, emits completed chunks into `VectorReadInfo`, and advances to the next request or response segment.

At multipart boundaries, `Write` assembles CRLF-delimited lines across callbacks, tolerates blank lines before boundaries, recognizes the terminating boundary, reads MIME-style part headers, and requires a valid `Content-Range` header for each non-final segment. Bad boundaries, malformed headers, missing ranges, negative lengths, or impossible buffer progress call `FailCallback`, which records a callback error for the worker to convert into an XRootD failure.

## State and persistence behavior

There is no durable persistence. Runtime state is per-operation and owns only the `VectorReadInfo`; the actual target buffers remain owned by the XRootD caller through `ChunkInfo` pointers. `m_chunk_list` may grow when a server response covers only part of a requested chunk; the remainder is appended as a new request entry backed by the original buffer pointer plus offset.

## Dependencies and integration points

The file depends on libcurl callbacks through `CurlOperation`, XRootD `ChunkList`, `ChunkInfo`, `VectorReadInfo`, `AnyObject`, and `XRootDStatus`, and on `HeaderParser` for status, multipart separator, and range metadata. It is produced by file/filesystem readv paths and executed by `CurlWorker`.

## Risks and edge cases

The multipart parser is strict: it fails on missing `Content-Range`, invalid boundaries, unsupported range units, out-of-range numeric values, and malformed header lines. The `std::stoll(value.data(), &count)` usage relies on curl-provided CRLF-backed buffers being safely terminated before parse overrun, which is subtle. Status `200` is treated as enough data to satisfy requested chunks from offset zero; sparse reads against servers that ignore multi-range requests can waste data or produce short results depending on response length. Out-of-order, coalesced, and partial ranges are supported, but overlapping or duplicate requested ranges depend on `CalculateNextBuffer` choosing the least-skip match.

## Test signals

The class exposes `SetSeparator`, `SetStatusCode`, and public `Write` for unit testing. Useful tests should cover single full response, single `Content-Range`, multipart responses split across callbacks, out-of-order/coalesced parts, malformed boundaries, missing or invalid `Content-Range`, zero-length requested chunks, and partial responses that append remainder chunks. No focused test file for this class was found in the checkout.
