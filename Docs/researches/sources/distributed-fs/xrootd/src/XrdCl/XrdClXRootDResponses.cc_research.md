# sources/distributed-fs/xrootd/src/XrdCl/XrdClXRootDResponses.cc

## Purpose
`XrdClXRootDResponses.cc` implements the response model classes declared in `XrdClXRootDResponses.hh`. It parses textual and binary protocol response payloads into typed objects such as locations, stat information, directory listings, page read info, page-write retry info, and response-handler wrappers.

## Important APIs, Types, And Functions
- `LocationInfo::ParseServerResponse` and `ProcessLocation` parse space-separated location tokens into manager/server and access-type records.
- `StatInfoImpl::ParseServerResponse` parses normal and extended stat fields, including optional checksum bracket notation; public `StatInfo` accessors expose id, size, flags, times, mode, owner, group, and checksum state.
- `StatInfoVFS::ParseServerResponse` parses six VFS capacity/utilization fields.
- `DirectoryList::ParseServerResponse` handles normal line-separated entries and `kXR_dstat` style alternating entry/stat lines; `HasStatInfo` detects the stat-prefixed format.
- `PageInfo` wraps page/chunk offset, length, data buffer, CRC32C checksums, and repaired page count using a movable pimpl.
- `RetryInfo` wraps page offsets and lengths that need retransmission after `pgwrite` checksum errors.
- `ResponseHandler::Wrap` creates self-deleting response handlers from lambdas, with overloads for reference-style and pointer-style callbacks.

## Control Flow
Parser methods validate null/empty input, split payloads, convert numeric fields with `strtoll`/`strtol`, and return boolean success/failure. `DirectoryList` selects normal or stat-aware parsing based on a fixed prefix, constructs `ListEntry` objects, and attaches `StatInfo` to statful entries. `PageInfo` and `RetryInfo` are thin containers used by `XRootDMsgHandler::ParseResponse`. Lambda wrappers call user functions and delete themselves only on final responses, treating `suContinue` as partial.

## State And Persistence Behavior
All state is process memory in typed response objects. `StatInfo` uses a unique pimpl to keep implementation fields private while supporting copy construction. `DirectoryList` owns and deletes `ListEntry*` elements. `PageInfo` stores a raw buffer pointer but does not delete it in the destructor; buffer ownership is handled by consumers such as `XCpSrc::DeleteChunk` or higher-level read APIs. `ResponseHandler::Wrap` transfers ownership of status/response to `unique_ptr` only in the reference-style overload; the pointer-style overload passes raw ownership to the callback.

## Dependencies And Integration Points
This implementation depends on `XrdClXRootDResponses.hh`, logging/default environment headers, constants, `Utils::splitString`, C library conversion functions, and protocol constants. It is consumed by `XRootDMsgHandler` parsers and user-facing XrdCl response APIs.

## Risks And Edge Cases
- `StatInfoImpl` optional checksum parsing checks `chunks[11]` when `chunks.size() >= 10`; malformed responses with 10 or 11 fields could index out of bounds.
- `DirectoryList::ParseServerResponse` can leak objects on parse failure after adding entries because it returns false before local cleanup, relying on destructor only if the caller deletes the list.
- `PageInfo` raw buffer ownership is non-obvious and must match producer/consumer conventions.
- `ResponseHandler::Wrap` self-deletes on final response; callbacks must not retain the wrapper pointer.
- Numeric parsing accepts base auto-detection; unusual prefixes can affect interpretation.

## Test Signals
Tests should cover valid/invalid location tokens, stat parsing with minimal, extended, and checksum forms, malformed optional checksum field counts, VFS stat field conversion errors, directory lists with and without stat info and odd stat entry counts, `PageInfo` move assignment preserving buffer pointer and checksum vector, `RetryInfo` indexing, and lambda wrappers for partial versus final responses.
