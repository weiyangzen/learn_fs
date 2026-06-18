# sources/distributed-fs/xrootd/src/XrdCl/XrdClAsyncRawReaderIntfc.hh

Purpose: declares the common base for asynchronous raw-body readers used by regular reads, vector reads, discard/error handling, and related protocols.

Important APIs/types: `SetDataLength(int)`, `SetChunkList(ChunkList*)`, pure virtual `Read()` and `GetResponse()`, helper `ReadBytesAsync`, `ChunkStatus`, `buffer_t`, and shared `Stage` enum.

Control flow/state: `ReadBytesAsync` loops on `Socket::Read` until the requested segment is filled or the socket returns `suRetry`/error. Shared mutable state tracks the response data length, bytes read from the current message, total raw bytes, chunk index/offset/remaining length, per-chunk status, discard buffer, and `dataerr`. Dependencies are URL/message/socket/status/logging types. Integration point is `AsyncMsgReader` raw handler logic. Risks: derived classes must reset inherited fields consistently; `SetChunkList` only resizes status when chunks are non-null; partial-read counters are easy to misuse. Test signals: retry preservation, chunk-list setup, zero/short reads, and derived reader error states.
