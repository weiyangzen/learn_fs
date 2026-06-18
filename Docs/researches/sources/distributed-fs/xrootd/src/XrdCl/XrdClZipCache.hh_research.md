# sources/distributed-fs/xrootd/src/XrdCl/XrdClZipCache.hh

## Purpose
`XrdClZipCache.hh` defines `ZipCache`, a small stateful zlib inflate coordinator used by `ZipArchive` when reading compressed ZIP members. It bridges asynchronous underlying archive reads, which may complete out of order, with ordered consumer read requests that must receive decompressed bytes in stream order.

## Important APIs and Types
`ZipError` carries an `XRootDStatus` when zlib initialization fails. `ZipCache` exposes `QueueReq(offset, length, buffer, handler)` for consumer read requests and `QueueRsp(status, offset, buffer)` for compressed input chunks returned by lower-level archive reads. Internal tuple types model pending requests and read responses. Responses are kept in a priority queue sorted by compressed offset, while requests are a FIFO queue.

## Control Flow
Construction initializes `z_stream` via `inflateInit2(&strm, -MAX_WBITS)`, intentionally using raw deflate mode without gzip headers. Both queue entry points lock `mtx`, add work, and call `Decompress`. `Decompress` chooses the next output request, accepts the next compressed response only when its offset equals `inabsoff`, checks response status, calls `inflate(Z_SYNC_FLUSH)`, advances the absolute compressed input offset by consumed bytes, fulfills a request when output is exhausted, and pops a response when input is fully consumed.

## State and Persistence
All state is in memory: the zlib stream, mutex, `inabsoff`, FIFO read requests, and pending out-of-order read responses. There is no disk persistence. The cache assumes a single logical inflate stream and ordered consumer offsets; it preserves decompression continuity across multiple queued requests.

## Dependencies and Integration Points
The file depends on zlib, XrdCl response types (`XRootDStatus`, `ChunkInfo`, `AnyObject`, `ResponseHandler`), STL containers, mutexes, and tuples. `ZipArchive` owns a `ZipCache` per archive member in `zipcache_t`.

## Risks and Test Signals
The critical risks are callback ownership, out-of-order compressed input, zlib return-code mapping, and deadlock/reentrancy from invoking handlers while state is locked. Tests should exercise response reordering, error responses before and after queued requests, truncated/corrupt deflate streams, exact output buffer boundaries, `Z_BUF_ERROR` continuation behavior, and multiple sequential requests over one compressed stream.
