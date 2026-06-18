# sources/distributed-fs/xrootd/src/XrdClHttp/XrdClHttpResponses.hh

## Purpose

This public header defines response wrapper classes that carry `ResponseInfo` alongside normal XRootD response payloads when the file or filesystem property `XrdClResponseInfo` is set to `"true"`.

## Important APIs, types, and functions

`ResponseInfoProperty` names the opt-in property. `DirectoryListResponse`, `StatResponse`, `QueryResponse`, `OpenResponseInfo`, `DeleteResponseInfo`, `MkdirResponseInfo`, and `ReadResponseInfo` each store a `std::unique_ptr<ResponseInfo>` and expose `GetResponseInfo`/`SetResponseInfo`. Some derive from existing XRootD response classes (`DirectoryList`, `StatInfo`, `Buffer`, `ChunkInfo`); open/delete/mkdir use standalone virtual classes.

## Control flow

Operation success paths decide whether to allocate a wrapper based on `SendResponseInfo()`. They move the operation's accumulated `ResponseInfo` into the wrapper and return it in `AnyObject`. Callers that opt in are responsible for extracting the derived response type and consuming the response-info pointer.

## State and persistence behavior

Response-info state is transferred by move and is not durable. The comment notes that not all XRootD base response classes have virtual destructors; if objects are deleted through base pointers without extracting response-info, memory can leak.

## Dependencies and integration points

The header depends on XRootD response classes and `XrdClHttpResponseInfo.hh`. It is used by stat, listdir, query, open, delete, mkdir, checksum, and read paths.

## Risks and edge cases

The opt-in contract is subtle: callers must know when a returned object is a derived wrapper and must release embedded response info. ABI compatibility matters because this is public plugin-facing API. Mixed use of base and derived response objects can cause casts to fail if the property was not set.

## Test signals

Tests should cover every response wrapper type, property-enabled and property-disabled paths, ownership transfer from `GetResponseInfo`, and safe deletion/extraction behavior. No direct tests were found.
