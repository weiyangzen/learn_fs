
# sources/distributed-fs/xrootd/src/XrdHttp/XrdHttpReadRangeHandler.cc

## Purpose

`XrdHttpReadRangeHandler.cc` implements HTTP Range header parsing and converts client byte ranges into bounded XRootD `read` or `readv` requests. It also tracks returned bytes across short reads, split chunks, and multipart response boundaries so `XrdHttpReq` can send correct single-range or multipart/byteranges output.

## Important APIs, Types, And Functions

- `Configure(Eroute, parms, cfg)` parses `XRD_READV_LIMITS`-style values `<readv_ior_max>,<readv_iov_max>` into `Configuration`.
- `getError()`, `isFullFile()`, `getMaxRanges()`, `isSingleRange()`, and `ListResolvedRanges()` expose current request interpretation and error state.
- `ParseContentRange(line)` parses the HTTP `Range:` value. Despite the name, it accepts strings like `bytes=15-17,20-25`.
- `SetFilesize(fs)` supplies file length before resolving open-ended or suffix ranges.
- `NextReadList()` returns the next `XrdHttpIOList` to issue through bridge `read`/`readv`.
- `NotifyReadResult(ret, urp, start, allend)` advances handler state after bytes arrive and reports multipart boundary conditions.
- `NotifyError()` forces a generic error state.
- Private helpers `parseOneRange()`, `rangeFig()`, `resolveRanges()`, `splitRanges()`, and `trimSplit()` parse, normalize, split, and retry ranges.

## Control Flow

The handler begins with `reset()` for each HTTP request. Header parsing stores raw `UserRange` entries with possibly missing start or end offsets. Later, after file open/stat, `SetFilesize()` records the size. On the first call to `isSingleRange()`, `ListResolvedRanges()`, or `NextReadList()`, `resolveRanges()` translates raw ranges into absolute inclusive offsets using the file size, clamps ranges that extend past EOF, skips ranges beyond EOF, adds a full-file range when no Range header exists and the file is non-empty, and sets HTTP 416 when all requested ranges miss the file.

`NextReadList()` lazily splits resolved user ranges. If a previous split was partially read, it calls `trimSplit()` to remove acknowledged data and reissue the remaining portion; if no bytes were read for a nonempty pending split, it sets a 500 error to avoid infinite retries. `splitRanges()` uses one large `kXR_read` for full-file or single-range reads and packs multiple bounded chunks for multi-range `kXR_readv`, honoring `vectorReadMaxChunkSize_`, `vectorReadMaxChunks_`, and `rRequestMaxBytes_`.

`NotifyReadResult()` validates that ranges are resolved and a split is active, advances current split and resolved range offsets, detects crossing chunk or user-range boundaries, and reports whether the returned bytes start a user range or finish all user ranges. `XrdHttpReq` uses these flags to insert multipart headers and final boundaries.

## State And Persistence

All state is per handler instance and reset per request: raw ranges, resolved ranges, current split list, file size, split cursors, response cursors, and error state. There is no persistence beyond the `XrdHttpReq` that owns the handler. `reset()` clears and `shrink_to_fit()`s vectors, which releases capacity but may increase churn under repeated requests.

## Dependencies And Integration Points

The implementation depends on `XrdHttpUtils.hh` for `XrdHttpIOList`, `XrdOuca2x` for config parsing, `XrdOucTUtils::splitString`, `XrdOucUtils::trim`, C string tokenization, and standard containers. `XrdHttpReq.cc` calls it during header parsing, open/stat post-processing, GET header formation, read scheduling, read callback handling, and footer error handling.

## Risks And Edge Cases

- `ParseContentRange()` uses `strdup(line)` without checking allocation failure and assumes `line` is non-null.
- Invalid syntax clears all raw ranges and deliberately ignores the header, matching HTTP behavior, but callers cannot distinguish invalid range syntax from no Range header.
- `rangeFig()` accepts negative values from `strtoll()`; later logic does not explicitly reject negative start/end values.
- `filesize_` defaults to zero. Calling resolve paths before `SetFilesize()` can classify all explicit ranges as unsatisfiable.
- `splitRanges()` calls `isSingleRange()`, which may call `resolveRanges()` recursively only when unresolved; current state prevents infinite recursion but the coupling is subtle.
- `NotifyReadResult()` assumes bridge results arrive in the same order and sizes do not cross split or user-range boundaries.
- Repeated `shrink_to_fit()` in `reset()` may be expensive under high request rate.
- The hardcoded 500 errors for internal range tracking failures are appropriate for server issues but can obscure backend short-read behavior.

## Test Signals

Unit tests should cover no Range header, empty file, closed ranges, suffix ranges, open-ended ranges, overlapping and out-of-order multi-ranges, ranges beyond EOF, malformed headers ignored as full-file, `XRD_READV_LIMITS` parsing, negative values, split limits, partial read retry through `trimSplit()`, zero-byte read protection, `NotifyReadResult()` boundary flags, readv ordering assumptions, and 416 error generation.
