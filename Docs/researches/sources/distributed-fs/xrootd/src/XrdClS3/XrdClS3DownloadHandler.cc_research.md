# sources/distributed-fs/xrootd/src/XrdClS3/XrdClS3DownloadHandler.cc

## Purpose

This file implements `XrdClS3::DownloadUrl`, a helper that downloads an HTTP/S3-backed object completely into an `XrdCl::Buffer` using the existing HTTP file plugin. It is used by S3 filesystem operations that need full XML/listing/stat-like responses.

## Important APIs, types, and functions

The anonymous `S3DownloadHandler` owns an opened `XrdCl::File`, caller handler, cumulative buffer, and expiry time. Its nested `ReadHandler` handles each async read result and schedules the next read. Its nested `CloseHandler` reports either a read error, close error, or final buffer. `GetTimeout` returns remaining seconds and whether the deadline is still valid. `DownloadUrl` creates an `XrdCl::File`, forces plugin object creation with an initial `Open(... Compress ...)`, sets HTTP header callout and full-download properties, then performs the real async read open with `S3DownloadHandler`.

## Control flow

On open success, `S3DownloadHandler::HandleResponse` starts a read at offset zero for 32 KiB. Each `ReadHandler` checks remaining time, closes and reports on read error, validates `ChunkInfo`, treats a zero-length chunk as EOF, shrinks the buffer to used size, closes the file, and finally returns the buffer. Non-zero chunks advance the cursor, grow the buffer by another 32 KiB, and issue the next read at the current cursor offset.

`CloseHandler` prefers the original read error over close status. On successful close after EOF, it wraps the owned buffer in an `AnyObject` with ownership transfer and calls the original handler.

## State and persistence behavior

State is transient and heap-owned through self-owning response handlers. The cumulative buffer grows to the full object size in memory. No data is persisted to disk. The helper stores a raw header-callout pointer in an HTTP file property as a hexadecimal integer string so the underlying HTTP plugin can invoke S3 signing.

## Dependencies and integration points

The implementation depends on `XrdCl::File`, `XrdCl::Buffer`, response handlers, default request timeout, XRootD open/read/close APIs, and HTTP plugin properties `XrdClHttpHeaderCallout` and `XrdClHttpFullDownload`. It integrates with `XrdClS3Filesystem.cc` listing/stat flows.

## Risks and edge cases

Full downloads can consume large memory because the buffer grows until EOF with no explicit cap. The first dummy open is a hack to force plugin object creation before setting properties; changes in XRootD plugin creation behavior could break this assumption. Timeout is checked between async callbacks, not during an individual HTTP read. The pointer-to-string callout bridge requires the referenced callout object to outlive the HTTP operation.

## Test signals

Tests should cover open failure, timeout before read, read error followed by close, missing `ChunkInfo`, zero-length EOF, close failure, multi-chunk accumulation, header-callout property propagation, and large object memory behavior. No direct tests were found.
