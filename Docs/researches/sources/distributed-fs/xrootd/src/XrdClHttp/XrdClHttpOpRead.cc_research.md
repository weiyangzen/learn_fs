# sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpOpRead.cc

## Purpose
`XrdClHttpOpRead.cc` implements scalar HTTP GET reads and page reads. `CurlReadOp` supports normal range reads plus prefetch continuations; `CurlPgReadOp` converts successful reads to page-checksummed responses.

## Important APIs and Functions
`CurlReadOp::Setup` installs write callback/data, chooses curl buffer size for large reads, and adds an inclusive `Range` header unless length is `UINT64_MAX`. `Continue` supplies a new client buffer to a paused prefetch GET and drains any overflow buffer. `Write` validates multipart and offset headers, copies response bytes to the client buffer, stores overflow bytes when libcurl delivers more than the current buffer can hold, and pauses when no buffer is available. `DeliverResponse`, `Pause`, `Success`, `Fail`, `ContinueHandle`, and `ReleaseHandle` manage callback and curl lifecycle. `CurlPgReadOp::Success` computes CRC32C per page and returns `PageInfo`.

## Control Flow
Standalone reads finish after one requested range. Prefetch reads issue a larger GET and repeatedly pause as each client buffer is filled; continuations unpause the same curl handle. Error bodies are captured separately in `m_err_msg` and are not copied to the client buffer.

## State and Persistence
The operation is read-only. In-memory state includes requested offset/length, bytes written, current buffer pointer/size, overflow buffer and offset, object offset within a prefetch stream, default handler, error body, and continue queue.

## Dependencies and Integration Points
It depends on `CurlOperation`, libcurl callbacks, `File::ReadPrefetch`, `HandlerQueue`, XrdCl `ChunkInfo`/`PageInfo`, CRC utilities, and page-size constants.

## Risks and Test Signals
Key risks are offset validation against server `Content-Range`, unsupported multipart byteranges, overflow buffer correctness, paused transfer timeouts without active handlers, and page checksum coverage for partial pages. Tests should cover zero-length reads, full-object reads, range header endpoints, short reads, oversized server responses, continuation after done, error body capture, and page checksums.
