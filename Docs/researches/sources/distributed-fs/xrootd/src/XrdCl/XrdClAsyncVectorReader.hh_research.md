# sources/distributed-fs/xrootd/src/XrdCl/XrdClAsyncVectorReader.hh

Purpose: reads vector-read responses composed of repeated `readahead_list` records followed by raw data for the matching requested chunks.

Important APIs: constructor, `Read(Socket&, uint32_t&)`, `GetResponse(AnyObject*&)`, and inherited raw-reader state. Extra state is `rdlstoff`, current `readahead_list`, and `rdlstlen`.

Control flow/state: `ReadStart` prepares to read a chunk header. `ReadRdLst` validates enough message bytes remain, reads and byte-swaps `rlen`/`offset`, finds the matching caller chunk, then `ReadRaw` reads the chunk payload while checking message boundaries. Completed chunks are marked in `chstatus`; `GetResponse` requires all chunks done and returns `VectorReadInfo`. Malformed boundaries or unmatched chunks cause `errCorruptedHeader` and reconnect. Dependencies are socket, response structs, chunk lists, logging, and byte-order helpers. Risks: O(n) chunk lookup per response chunk, duplicate chunk ambiguity, strict exact offset/length matching, and boundary validation. Test signals: multi-chunk response, reordered chunks, partial header/body retry, missing chunk, oversized declared chunk, and all-done validation.
