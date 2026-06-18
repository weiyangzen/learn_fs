
# sources/distributed-fs/xrootd/src/XrdHttp/XrdHttpReadRangeHandler.hh

## Purpose

`XrdHttpReadRangeHandler.hh` declares the request-local helper that interprets HTTP Range headers and manages the read scheduling/acknowledgement state for GET responses. It hides the details of HTTP byte-range normalization and XRootD read/readv chunking behind a compact API consumed by `XrdHttpReq`.

## Important APIs, Types, And Functions

- Constants `READV_MAXCHUNKS`, `READV_MAXCHUNKSIZE`, and `RREQ_MAXSIZE` provide default limits of 512 chunks, 512 KiB per readv chunk, and 8 MiB per whole read request.
- `struct Configuration` optionally overrides chunk size, number of chunks, and total request size.
- `struct Error` stores an HTTP return code and message with `operator bool()` for error presence.
- `struct UserRange` represents raw or resolved ranges with independent start/end presence flags.
- `using UserRangeList` aliases `std::vector<UserRange>`.
- Public methods include constructor, static `Configure()`, `getError()`, `getMaxRanges()`, `isFullFile()`, `isSingleRange()`, `ListResolvedRanges()`, `NextReadList()`, `NotifyError()`, `NotifyReadResult()`, `ParseContentRange()`, `reset()`, and `SetFilesize()`.
- Private state fields track raw ranges, resolved ranges, split read chunks, file size, and multiple cursor offsets for both issued chunks and received data.

## Control Flow

Construction sets default limits or configured limits, then resets state. The expected call order is: `ParseContentRange()` during header parsing, `SetFilesize()` after open/stat, `ListResolvedRanges()` or `NextReadList()` to resolve and split, repeated bridge reads using returned `XrdHttpIOList`, and `NotifyReadResult()` for every received data segment. `reset()` makes the instance reusable for the next HTTP request.

## State And Persistence

State is entirely in the object. The handler owns all vectors it returns references to; callers must treat references as invalid after `reset()` or the next splitting call. `Error` state is sticky until reset. The referenced `Configuration` is copied into scalar limits by the constructor, so the caller does not need to keep the configuration object alive despite the comment saying otherwise.

## Dependencies And Integration Points

The header includes `XrdHttpUtils.hh`, `vector`, and `string`, and references `XrdSysError` through the `Configure()` declaration via included dependencies. The central integration is `XrdHttpReq`, which owns a handler instance and uses it to decide `kXR_seqio`, build GET headers, choose read versus readv, format multipart bodies, and decide trailer errors.

## Risks And Edge Cases

- Comments contain a few terminology errors (`Content-Range` versus `Range`, "Incidcates", "eiter"), which can mislead maintainers but not runtime behavior.
- Public methods return const references to internal containers, so caller lifetime discipline matters.
- `SetFilesize()` must occur before resolution; after resolution, changing file size is an error.
- The API does not expose whether a malformed Range header was ignored.
- Offsets use `off_t`, but chunk sizes are `size_t` and `int` in places; very large files/ranges need careful conversion tests.

## Test Signals

API-level tests should validate constructor defaults and overrides, reference invalidation expectations, sticky errors, call-order errors such as `SetFilesize()` after resolution, and `getMaxRanges()` behavior before file size is known. Integration tests should confirm `XrdHttpReq` chooses `kXR_seqio` only when `getMaxRanges() <= 1`.
