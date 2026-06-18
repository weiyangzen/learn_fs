# sources/distributed-fs/xrootd/src/XrdCl/XrdClAsyncPageReader.hh

Purpose: reads page-read responses where each page of user data is preceded by a CRC32C digest. It fills caller-provided chunks and a digest vector using scatter/gather I/O.

Important APIs/types: constructor sizing `digests`, `SetRsp(ServerResponseV2*)`, `Read(Socket&, uint32_t&)`, and private IOV helpers `CalcRdSize`, `InitIOV`, `ShiftIOV`, `shiftdgbuf`, and `shiftpgbuf`. It uses `ChunkList`, `iovec`, `XrdOucPgrwUtils`, and `XrdSys::PageSize`.

Control flow/state: `SetRsp` maps response offset into chunk/digest indices. `Read` initializes an alternating digest/page iovec, calls `Socket::ReadV`, converts completed digest words with `ntohl`, advances chunk and digest cursors, and returns `suRetry` on partial progress. State is in response length, chunk index/offset, digest index/offset, and current iovec. Risks: off-by-one/page alignment bugs, digest buffer bounds, and iov limit assumptions. Test signals: unaligned first/last page, multi-chunk reads, partial ReadV progress, digest byte-order conversion, and zero-length responses.
