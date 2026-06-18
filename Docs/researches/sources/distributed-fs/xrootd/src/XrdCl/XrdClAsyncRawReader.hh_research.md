# sources/distributed-fs/xrootd/src/XrdCl/XrdClAsyncRawReader.hh

Purpose: reads raw body data for regular read responses into caller-provided chunks and produces the user-visible read response object.

Important APIs: constructor, `Read(Socket&, uint32_t&)`, `GetResponse(AnyObject*&)`, private `GetChunkInfo()` and `GetVectorReadInfo()`. It inherits buffer/state fields from `AsyncRawReaderIntfc`.

Control flow/state: `ReadStart` initializes the first chunk, `ReadRaw` bounds reads to response `dlen`, calls `ReadBytesAsync`, advances chunk/message counters, and moves to the next chunk. If the response has more data than supplied buffer space, it reports corrupted header rather than trying to resynchronize. `GetResponse` returns `ChunkInfo` for normal read or `VectorReadInfo` for virtual readv. Dependencies are socket, stream response structs, status, and logs. Risks: buffer-size mismatch, chunk index bounds, and total byte accounting. Test signals: partial reads, multi-chunk fill, too-small buffer error, virtual readv response mapping, and invalid response after `dataerr`.
